import os
import smtplib
import logging
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2 import service_account
from google.cloud import monitoring_v3, compute_v1
from google.auth.transport.requests import Request

from utils.logging import setup_logging, logger

# Initialize logging
setup_logging()
logger = logging.getLogger('gcp_monitor')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
project_id = os.getenv("PROJECT_ID")
instance_name = os.getenv("INSTANCE_NAME")
zone = os.getenv("ZONE") 
sender_email = os.getenv("SENDER_EMAIL")
app_password = os.getenv("APP_PASSWORD")
receiver_email = os.getenv("RECEIVER_EMAIL")

def get_google_credentials(credentials_path=None):
    """
    Get Google Cloud credentials from a service account JSON file.
    
    Args:
        credentials_path (str, optional): Path to the credentials JSON file.
            If not provided, looks for 'credentials.json' in the current directory.
    
    Returns:
        service_account.Credentials: Authenticated credentials object
        
    Raises:
        FileNotFoundError: If credentials file is not found
        ValueError: If credentials are invalid
    """
    if credentials_path is None:
        credentials_path = os.path.join(os.path.dirname(__file__), 'credentials.json')
    
    try:
        if not os.path.exists(credentials_path):
            logger.error(f"Credentials file not found at: {credentials_path}")
            raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
            
        logger.info(f"Loading credentials from: {credentials_path}")
        return service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
    except Exception as e:
        logger.error(f"Failed to load credentials from {credentials_path}: {str(e)}")
        raise

# Initialize credentials once and reuse
credentials = None
try:
    credentials = get_google_credentials()
    logger.info("Successfully loaded Google Cloud credentials")
except Exception as e:
    logger.error(f"Failed to initialize Google Cloud credentials: {str(e)}")
    raise


def get_cpu_utilization(project_id, instance_id, zone, minutes=60):
    """
    Get the average CPU utilization for a specific instance.
    
    Args:
        project_id (str): GCP project ID
        instance_id (str): Instance ID to check
        zone (str): Zone where the instance is located
        minutes (int): Time range in minutes to check
        
    Returns:
        float: Average CPU utilization percentage
    """
    global credentials
    try:
        if not credentials:
            credentials = get_google_credentials()
        client = monitoring_v3.MetricServiceClient(credentials=credentials)
        
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=minutes)
        
        interval = monitoring_v3.TimeInterval({
            "end_time": now,
            "start_time": start_time,
        })
        
        # Build the filter for the specific instance
        filter_str = (
            f'metric.type = "compute.googleapis.com/instance/cpu/utilization" '
            f'AND resource.labels.instance_id = "{instance_id}"'
        )
        
        # Make the API request
        results = client.list_time_series(
            request={
                "name": f"projects/{project_id}",
                "filter": filter_str,
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        # Calculate average utilization
        total_utilization = 0.0
        data_points = 0
        
        for series in results:
            for point in series.points:
                total_utilization += point.value.double_value
                data_points += 1
        
        avg_utilization = (total_utilization / data_points * 100) if data_points > 0 else 0.0
        return avg_utilization
        
    except Exception as e:
        logger.error(f"Error getting CPU utilization for instance {instance_id}: {str(e)}")
        return 0.0

def send_email_alert(data, sender_email, receiver_email, app_password):
    list_of_body=[]
    subject = "⚠️ GCP Low Memory Alert"
    for i in data:    

        body=f"""
        <b>GCP Alert:</b><br>
        Instance <code>{i[0]}</code> in zone <code>{i[1]}</code> is underutilized.<br>
        Memory Usage: <b>{i[2]:.2f}%</b><br><br>
        <i>It has been automatically stopped to save resources.</i>
        """
        list_of_body.append(body)
    splitted_body=' '.join(list_of_body)
    print(splitted_body)
    
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    for v in list_of_body:
       msg.attach(MIMEText(v, "html"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, app_password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()


def main():
    """
    Main function to monitor GCP instances and send alerts.
    """
    global credentials
    try:
        logger.info("Starting GCP instance monitoring")
        
        # Get list of all instances
        if not credentials:
            credentials = get_google_credentials()
        compute = compute_v1.InstancesClient(credentials=credentials)
        
        # Get instances in the specified zone
        instances = compute.list(project=project_id, zone=zone)
        
        underutilized_instances = []
        
        # Check each instance's CPU utilization
        for instance in instances:
            instance_id = instance.id
            utilization = get_cpu_utilization(project_id, instance_id, zone)
            
            logger.debug(f"Instance {instance_id} - CPU: {utilization:.2f}%")
            
            # Check if utilization is below threshold (20%)
            if utilization < 20.0:
                underutilized_instances.append((instance_id, zone, utilization))
        
        # Send alert if needed
        if underutilized_instances:
            logger.info(f"Found {len(underutilized_instances)} underutilized instances")
            logger.info(f"Sending email alert to {receiver_email}")
            send_email_alert(underutilized_instances, sender_email, receiver_email, app_password)
        else:
            logger.info("No underutilized instances found")
            
    except Exception as e:
        logger.error(f"Error in main: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()
