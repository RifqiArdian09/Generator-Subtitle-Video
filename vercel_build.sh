#!/bin/bash

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y ffmpeg

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p /tmp/uploads
mkdir -p static
mkdir -p templates

# Set environment variables
export FLASK_APP=api/index.py
export FLASK_ENV=production

# Install Python 3.9 if not present
if ! command -v python3.9 &> /dev/null; then
    echo "Installing Python 3.9..."
    apt-get install -y python3.9 python3.9-distutils
fi

echo "Build completed successfully!"
