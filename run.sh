#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to detect the operating system
get_os() {
    case "$(uname -s)" in
        Linux*)     echo "Linux" ;;
        Darwin*)    echo "Mac" ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*) echo "Windows" ;;
        *)          echo "Unknown" ;;
    esac
}

# Function to install dependencies on Linux
install_linux_deps() {
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv nginx
    elif command -v dnf &> /dev/null; then
        # Fedora
        sudo dnf install -y python3 python3-pip python3-venv nginx
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        sudo yum install -y python3 python3-pip python3-venv nginx
    elif command -v pacman &> /dev/null; then
        # Arch Linux
        sudo pacman -Syu --noconfirm python python-pip python-virtualenv nginx
    else
        log "${YELLOW}Warning: Could not determine package manager. Please install Python 3, pip, and nginx manually.${NC}"
    fi
}

# Function to install dependencies on macOS
install_mac_deps() {
    if ! command -v brew &> /dev/null; then
        log "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    log "Installing dependencies..."
    brew update
    brew install python3 nginx
}

# Main execution
log "Detecting operating system..."
OS_TYPE=$(get_os)

case $OS_TYPE in
    Linux)
        log "Linux detected. Installing dependencies..."
        install_linux_deps
        ;;
    Mac)
        log "macOS detected. Installing dependencies..."
        install_mac_deps
        ;;
    Windows)
        log "Windows detected. Please use run.bat instead."
        exit 1
        ;;
    *)
        log "${RED}Error: Unsupported operating system.${NC}"
        exit 1
        ;;
esac

# Create virtual environment if it doesn't exist
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    log "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
log "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip and install dependencies
log "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if credentials.json exists
if [ -f "credentials.json" ]; then
    log "Using service account credentials from credentials.json"
    
    # Set the environment variable for Google Cloud SDK to find the credentials
    export GOOGLE_APPLICATION_CREDENTIALS="$(pwd)/credentials.json"
    
    # Also set the project ID from the environment variable if it exists
    if [ -n "$project_id" ]; then
        export CLOUDSDK_CORE_PROJECT="$project_id"
    fi
    
    log "Google Cloud credentials configured from credentials.json"
else
    log "${RED}Error: credentials.json not found in the current directory.${NC}"
    log "Please place your service account key file named 'credentials.json' in this directory."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Run the application
log "Starting GCP Monitor..."
if [ "$1" = "--background" ] || [ "$1" = "-b" ]; then
    nohup python3 main.py > logs/app.log 2>&1 &
    log "GCP Monitor is running in the background. Check logs/app.log for output."
    log "To stop the application, run: pkill -f 'python3 main.py'"
else
    log "${GREEN}Starting GCP Monitor in the foreground. Press Ctrl+C to stop.${NC}"
    python3 main.py
fi
