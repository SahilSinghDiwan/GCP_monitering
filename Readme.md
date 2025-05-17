# GCP Resource Monitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python-based monitoring solution for Google Cloud Platform (GCP) that identifies underutilized compute instances and sends email alerts. The tool helps optimize cloud costs by identifying resources that may be candidates for downsizing or termination.

## 🌟 Features

- **Automated Monitoring**: Continuously monitors CPU utilization of GCP compute instances
- **Smart Alerts**: Sends email notifications for underutilized instances
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Easy Setup**: Simple configuration using environment variables
- **Comprehensive Logging**: Detailed logs for troubleshooting and auditing
- **Resource Optimization**: Helps reduce cloud costs by identifying underutilized resources

## 📋 Prerequisites

- Python 3.6 or higher
- Google Cloud Platform (GCP) account with appropriate permissions
- GCP Service Account with Monitoring Viewer and Compute Viewer roles
- Gmail account for sending email alerts (or configure another SMTP server)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/SahilSinghDiwan/GCP_monitering.git
cd GCP_monitering
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# GCP Configuration
project_id=
instance_name=
zone=

# Email Configuration

sender_email=
app_password=
receiver_email=

```

> **Note**: For Gmail, you'll need to generate an App Password if you have 2FA enabled. Go to your Google Account > Security > App passwords.

### 3. Install Dependencies

#### Linux/macOS:

```bash
chmod +x run.sh
./run.sh
```

#### Windows:

```bash
run.bat
```

The script will automatically:

1. Install system dependencies
2. Set up a Python virtual environment
3. Install required Python packages
4. Start the monitoring service

## ⚙️ Configuration

### Environment Variables

| Variable                    | Description                                   | Required | Default   |
| --------------------------- | --------------------------------------------- | -------- | --------- |
| `project_id`                | Your GCP Project ID                           | ✅       | -         |
| `sender_email`              | Email address to send alerts from             | ✅       | -         |
| `app_password`              | App password for the sender email             | ✅       | -         |
| `receiver_email`            | Email address to receive alerts               | ✅       | -         |
| `CPU_UTILIZATION_THRESHOLD` | CPU usage threshold (0-1) to trigger alerts   | ❌       | 0.2 (20%) |
| `CHECK_INTERVAL_MINUTES`    | How often to check instance metrics (minutes) | ❌       | 60        |

### Running in Production

For production use, consider running the monitor as a background service:

#### Linux (systemd)

```bash
# Create a systemd service file
sudo tee /etc/systemd/system/gcp-monitor.service > /dev/null <<EOL
[Unit]
Description=GCP Resource Monitor
After=network.target

[Service]
User=your_username
WorkingDirectory=/path/to/gcp-resource-monitor
ExecStart=/path/to/gcp-resource-monitor/run.sh --background
Restart=always
Environment="PATH=/path/to/venv/bin"

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable gcp-monitor.service
sudo systemctl start gcp-monitor.service
```

## 📊 How It Works

1. The monitor queries the GCP Monitoring API for CPU utilization metrics
2. It calculates the average CPU usage for each instance over the specified time window
3. If an instance's average CPU usage is below the threshold, it's flagged as underutilized
4. An email alert is sent with details about underutilized instances
5. The process repeats at the specified interval

## 📝 Logs

Logs are stored in the `logs/` directory:

- `gcp_monitor.log`: Main application logs
- Rotated logs are automatically created when the file reaches 5MB (up to 5 backups)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Cloud Python Client Libraries](https://github.com/googleapis/google-cloud-python)
- [Python Logging](https://docs.python.org/3/library/logging.html)

---

<div align="center">
  Made with ❤️ by Sahil Singh Diwan
</div>
