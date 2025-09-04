#!/bin/bash

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p /tmp/uploads

echo "Build completed successfully!"