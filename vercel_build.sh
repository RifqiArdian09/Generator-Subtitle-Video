#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install FFmpeg
apt-get update && apt-get install -y ffmpeg

# Create necessary directories
mkdir -p uploads
mkdir -p static
mkdir -p templates

# Set environment variables
export FLASK_APP=subtitle_generator.py
export FLASK_ENV=production

# Make the script executable
chmod +x vercel_build.sh
