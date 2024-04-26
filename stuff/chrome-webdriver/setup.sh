#!/bin/bash

BASE_DIR="$HOME/setup-chrome"
mkdir -p "$BASE_DIR"
cd "$BASE_DIR"

# Update and install dependencies for headless operation
sudo apt update
sudo apt install -y xvfb libxi6 libgconf-2-4 libnss3

# Install Google Chrome if it's not already installed
if ! google-chrome-stable --version &>/dev/null; then
    echo "Installing Google Chrome..."
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo apt install ./google-chrome-stable_current_amd64.deb -y
else
    echo "Google Chrome is already installed."
fi

# Define the URL for the correct Chromedriver version
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/124.0.6367.91/linux64/chromedriver-linux64.zip"

# Download Chromedriver
echo "Downloading Chromedriver from $CHROMEDRIVER_URL..."
wget -N "$CHROMEDRIVER_URL"
if [ $? -ne 0 ]; then
    echo "Failed to download Chromedriver from URL: $CHROMEDRIVER_URL"
    exit 1
fi

# Unzip and move Chromedriver to the executable path
unzip -o chromedriver-linux64.zip
# Correct the path based on the actual structure of the zip file
sudo mv chromedriver-linux64/chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Cleanup
rm -rf chromedriver-linux64.zip chromedriver-linux64

echo "Chromedriver installed successfully."
