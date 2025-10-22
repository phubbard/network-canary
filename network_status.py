#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
Network Status Display for e-Paper
Displays network connectivity status on a 3.97" e-Paper display
"""

import sys
import os
import time
import socket
import subprocess
from typing import Tuple

# Add the waveshare library path
epaper_path = "/home/pfh/code/3in97_e-Paper_G/RaspberryPi_JetsonNano/python"
libdir = os.path.join(epaper_path, 'lib')
picdir = os.path.join(epaper_path, 'pic')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd3in97g
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetworkStatusDisplay:
    def __init__(self):
        """Initialize the e-Paper display"""
        self.epd = epd3in97g.EPD()
        self.width = 800
        self.height = 480

        # Load fonts (increased sizes for better readability)
        try:
            self.font_title = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
            self.font_statusbar = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 48)
            self.font_large = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 32)
            self.font_normal = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 26)
            self.font_small = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 20)
        except:
            # Fallback to default font if Font.ttc not available
            self.font_title = ImageFont.load_default()
            self.font_statusbar = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
            self.font_normal = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def check_ethernet_ip(self) -> Tuple[bool, str]:
        """Check if ethernet port has an IP address"""
        try:
            result = subprocess.run(['ip', 'addr', 'show', 'eth0'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'inet ' in line and not '127.0.0.1' in line:
                        ip = line.strip().split()[1].split('/')[0]
                        return True, ip
            return False, "No IP"
        except Exception as e:
            logger.error(f"Error checking ethernet IP: {e}")
            return False, "Error"

    def check_dns_server(self) -> Tuple[bool, str]:
        """Check if we can reach the default DNS server"""
        try:
            # Get DNS server from resolv.conf
            with open('/etc/resolv.conf', 'r') as f:
                for line in f:
                    if line.startswith('nameserver'):
                        dns_server = line.split()[1]
                        # Try to ping it
                        result = subprocess.run(['ping', '-c', '1', '-W', '2', dns_server],
                                              capture_output=True, timeout=3)
                        if result.returncode == 0:
                            return True, dns_server
                        return False, dns_server
            return False, "No DNS configured"
        except Exception as e:
            logger.error(f"Error checking DNS: {e}")
            return False, "Error"

    def check_hostname_resolution(self, hostname: str = "fratboy.phfactor.net") -> Tuple[bool, str]:
        """Check if we can resolve a local hostname"""
        try:
            ip = socket.gethostbyname(hostname)
            return True, ip
        except Exception as e:
            logger.error(f"Error resolving {hostname}: {e}")
            return False, "Failed"

    def check_gateway(self) -> Tuple[bool, str]:
        """Check if we can ping the default gateway"""
        try:
            result = subprocess.run(['ip', 'route', 'show', 'default'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        gateway = line.split()[2]
                        # Try to ping it
                        ping_result = subprocess.run(['ping', '-c', '1', '-W', '2', gateway],
                                                   capture_output=True, timeout=3)
                        if ping_result.returncode == 0:
                            return True, gateway
                        return False, gateway
            return False, "No gateway"
        except Exception as e:
            logger.error(f"Error checking gateway: {e}")
            return False, "Error"

    def check_internet_ip(self, ip: str = "8.8.8.8") -> Tuple[bool, str]:
        """Check if we can ping a well-known internet IP"""
        try:
            result = subprocess.run(['ping', '-c', '1', '-W', '2', ip],
                                  capture_output=True, timeout=3)
            return result.returncode == 0, ip
        except Exception as e:
            logger.error(f"Error pinging {ip}: {e}")
            return False, "Error"

    def check_internet_hostname(self, hostname: str = "amazon.com") -> Tuple[bool, str]:
        """Check if we can resolve a hostname (many sites block ICMP ping)"""
        try:
            # Just resolve - many major sites block ping for security
            ip = socket.gethostbyname(hostname)
            return True, ip
        except Exception as e:
            logger.error(f"Error resolving {hostname}: {e}")
            return False, "Failed"

    def run_all_checks(self) -> dict:
        """Run all network checks and return results"""
        logger.info("Running network checks...")

        checks = {
            "Ethernet IP": self.check_ethernet_ip(),
            "DNS Server": self.check_dns_server(),
            "Local Hostname": self.check_hostname_resolution("fratboy.phfactor.net"),
            "Gateway": self.check_gateway(),
            "Internet IP (8.8.8.8)": self.check_internet_ip("8.8.8.8"),
            "Internet DNS (amazon.com)": self.check_internet_hostname("amazon.com")
        }

        return checks

    def draw_status_display(self, checks: dict):
        """Draw the status display on the e-Paper"""
        # Create image
        image = Image.new('RGB', (self.width, self.height), self.epd.WHITE)
        draw = ImageDraw.Draw(image)

        # Draw title
        draw.text((20, 10), "Network Status Monitor",
                 font=self.font_title, fill=self.epd.BLACK)

        # Draw timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        draw.text((20, 50), f"Updated: {timestamp}",
                 font=self.font_small, fill=self.epd.BLACK)

        # Draw status lines
        y_position = 90
        all_passed = True

        for test_name, (passed, detail) in checks.items():
            # Status indicator (colored box)
            color = self.epd.BLACK if passed else self.epd.RED
            draw.rectangle([(20, y_position), (40, y_position + 20)], fill=color)

            # Status text
            status_text = "OK" if passed else "FAIL"
            status_color = self.epd.BLACK if passed else self.epd.RED
            draw.text((50, y_position), f"{status_text}: {test_name}",
                     font=self.font_normal, fill=status_color)

            # Detail text (moved further right to avoid overlap with larger fonts)
            draw.text((520, y_position), detail,
                     font=self.font_small, fill=self.epd.BLACK)

            y_position += 35

            if not passed:
                all_passed = False

        # Draw large status bar at bottom - red background with yellow text
        bar_height = 80
        bar_y = self.height - bar_height

        draw.rectangle([(0, bar_y), (self.width, self.height)], fill=self.epd.RED)

        # Draw status text on bar with yellow text for high visibility
        status_text = "ALL SYSTEMS OK" if all_passed else "NETWORK ISSUES DETECTED"

        # Center the text
        bbox = draw.textbbox((0, 0), status_text, font=self.font_statusbar)
        text_width = bbox[2] - bbox[0]
        text_x = (self.width - text_width) // 2

        draw.text((text_x, bar_y + 16), status_text,
                 font=self.font_statusbar, fill=self.epd.YELLOW)

        # Display on e-Paper
        logger.info("Updating display...")
        self.epd.display(self.epd.getbuffer(image))

    def run(self, update_interval: int = 60):
        """Main loop - run checks and update display periodically"""
        try:
            logger.info("Initializing e-Paper display...")
            self.epd.init()
            self.epd.Clear()

            # Use fast refresh mode for updates
            self.epd.init_Fast()

            iteration = 0
            previous_checks = None
            while True:
                logger.info(f"\n=== Update {iteration + 1} ===")

                # Run network checks
                checks = self.run_all_checks()

                # Check if all tests passed
                all_passed = all(passed for passed, _ in checks.values())

                # Extract just pass/fail status for comparison (ignore detail values like IPs that may rotate)
                current_status = {k: v[0] for k, v in checks.items()}
                previous_status = {k: v[0] for k, v in previous_checks.items()} if previous_checks else None

                # Determine if we need to update the display
                should_update = False
                if previous_checks is None:
                    # First run - always update
                    should_update = True
                    logger.info("First run - updating display")
                elif not all_passed:
                    # Something failed - always update
                    should_update = True
                    logger.info("Failures detected - updating display")
                elif current_status != previous_status:
                    # Pass/fail status changed - update
                    should_update = True
                    logger.info("Status changed - updating display")
                    # Log what changed for debugging
                    for key in current_status:
                        if current_status[key] != previous_status.get(key):
                            logger.info(f"  Status change: {key}: {previous_status.get(key)} -> {current_status[key]}")
                else:
                    # Everything still OK and status unchanged - skip update
                    logger.info("All tests OK and status unchanged - skipping display update to preserve e-ink")

                # Update display if needed
                if should_update:
                    self.draw_status_display(checks)

                # Store current results for next comparison
                previous_checks = checks.copy()

                logger.info(f"Waiting {update_interval} seconds until next update...")
                time.sleep(update_interval)

                iteration += 1

        except KeyboardInterrupt:
            logger.info("\nShutting down...")
            self.cleanup()
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.cleanup()
            raise

    def cleanup(self):
        """Clean up and put display to sleep"""
        try:
            logger.info("Putting display to sleep...")
            self.epd.init()  # Re-init for proper sleep
            self.epd.Clear()
            self.epd.sleep()
            epd3in97g.epdconfig.module_exit(cleanup=True)
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    display = NetworkStatusDisplay()

    # Get update interval from command line or use default 60 seconds (1 minute)
    update_interval = 60
    if len(sys.argv) > 1:
        try:
            update_interval = int(sys.argv[1])
            logger.info(f"Using update interval: {update_interval} seconds")
        except ValueError:
            logger.warning(f"Invalid interval '{sys.argv[1]}', using default 60 seconds")

    display.run(update_interval)
