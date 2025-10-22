#!/bin/bash
# Install Network Canary as a systemd service

set -e

echo "Installing Network Canary service..."

# Copy service file to systemd directory
sudo cp network-canary.service /etc/systemd/system/

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable network-canary.service

# Start the service now
sudo systemctl start network-canary.service

# Show status
echo ""
echo "Service installed and started!"
echo ""
echo "Useful commands:"
echo "  sudo systemctl status network-canary   # Check service status"
echo "  sudo systemctl stop network-canary     # Stop the service"
echo "  sudo systemctl start network-canary    # Start the service"
echo "  sudo systemctl restart network-canary  # Restart the service"
echo "  sudo journalctl -u network-canary -f   # View logs (live)"
echo "  sudo systemctl disable network-canary  # Disable auto-start on boot"
