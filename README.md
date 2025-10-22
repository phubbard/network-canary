# Network Canary

A network status monitor for Raspberry Pi with Waveshare 3.97" color e-Paper display (800x480). Displays real-time network connectivity status with intelligent display updates to preserve e-ink lifespan.

![picture of unit](canary.jpg)
## Features

- **Comprehensive Network Testing**
  - Ethernet IP address detection
  - DNS server connectivity
  - Local hostname resolution
  - Gateway (router) connectivity
  - Internet connectivity (8.8.8.8)
  - DNS resolution to internet hosts (amazon.com)

- **Smart Display Management**
  - Color-coded status indicators (green/black for OK, red for failures)
  - Large status bar for at-a-glance monitoring
  - Intelligent updates: only refreshes display when status changes
  - Preserves e-ink display lifespan by skipping unnecessary refreshes

- **Configurable Update Interval**
  - Default: 60 seconds (1 minute)
  - Customizable via command-line argument

## Hardware Requirements

- Raspberry Pi (tested on Raspberry Pi with Raspbian/Raspberry Pi OS)
- [Waveshare 3.97" e-Paper HAT (G)](https://www.waveshare.com/wiki/3.97inch_e-Paper_HAT+_(G)_Manual) - 800x480 color e-ink display
- Ethernet connection (monitors eth0 interface)

## Software Dependencies

- Python 3.x
- Waveshare e-Paper library
- PIL/Pillow
- Standard Linux networking tools (ip, ping)

## Installation

1. Install the Waveshare e-Paper library:
   ```bash
   # Follow instructions from:
   # https://www.waveshare.com/wiki/3.97inch_e-Paper_HAT+_(G)_Manual#Run_Python_Demo
   ```

2. Clone this repository:
   ```bash
   git clone git@github.com:phubbard/network-canary.git
   cd network-canary
   ```

3. Update the path in `network_status.py` if your Waveshare library is in a different location:
   ```python
   epaper_path = "/home/pfh/code/3in97_e-Paper_G/RaspberryPi_JetsonNano/python"
   ```

4. Make the script executable:
   ```bash
   chmod +x network_status.py
   ```

## Usage

### Basic usage (60-second updates):
```bash
./network_status.py
```

### Custom update interval (e.g., 30 seconds):
```bash
./network_status.py 30
```

### Stop the monitor:
Press `Ctrl+C` - the script will cleanly shut down and put the display to sleep.

## Display Layout

```
┌─────────────────────────────────────────────┐
│ Network Status Monitor                      │
│ Updated: 2025-10-21 23:45:00                │
│                                             │
│ ■ OK: Ethernet IP              192.168.1.100│
│ ■ OK: DNS Server               192.168.1.1  │
│ ■ OK: Local Hostname           10.0.0.50    │
│ ■ OK: Gateway                  192.168.1.1  │
│ ■ OK: Internet IP (8.8.8.8)    8.8.8.8      │
│ ■ OK: Internet DNS (amazon.com) 98.87.170.71│
│                                             │
│                                             │
│════════════════════════════════════════════│
│          ALL SYSTEMS OK                     │
└─────────────────────────────────────────────┘
```

- Green/Black boxes = Test passing
- Red boxes = Test failing
- Bottom bar: Green/Black when all OK, Red when any failures detected

## How It Works

The script runs in a continuous loop:

1. **Network Checks**: Runs all six network connectivity tests
2. **Status Comparison**: Compares pass/fail status with previous run
3. **Smart Update Decision**:
   - First run: Always updates display
   - Failures detected: Always updates display
   - Status changed (pass↔fail): Always updates display
   - All OK and unchanged: **Skips display refresh** to preserve e-ink

This intelligent update strategy significantly reduces wear on the e-ink display while ensuring problems are immediately visible.

## Configuration

Edit the following in `network_status.py` to customize:

- **Local hostname**: Change `fratboy.phfactor.net` to your local server
- **Internet test host**: Change `amazon.com` to another hostname
- **Internet test IP**: Change `8.8.8.8` to another public DNS server
- **Update interval**: Default is 60 seconds in the `run()` method
- **Font sizes**: Adjust in the `__init__()` method

## Logging

The script logs to stderr with INFO level messages:
- Network check results
- Display update decisions
- Status changes
- Any errors encountered

View logs with:
```bash
./network_status.py 2>&1 | tee network_canary.log
```

## Troubleshooting

**Display not updating**:
- Check hardware connections
- Verify Waveshare library path in script
- Check permissions for GPIO access (may need `sudo`)

**Network checks failing**:
- Verify interface name is `eth0` (or modify script)
- Check DNS configuration in `/etc/resolv.conf`
- Ensure ping is not blocked by firewall

**Script crashes**:
- Check Python version (requires 3.x)
- Verify all dependencies installed
- Review logs for specific error messages

## License

MIT License - see LICENSE file for details

## Credits

- Waveshare for the excellent e-Paper display and library
- Built for monitoring Raspberry Pi network connectivity

## Contributing

Issues and pull requests welcome at https://github.com/phubbard/network-canary
