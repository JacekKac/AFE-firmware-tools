# AFE Firmware Tools

This repository contains tools to scan and manage AFE Firmware devices on your local network.

## Features

- Scans your local subnet for AFE devices using Nmap
- Extracts device information from the web interface
- Fully plug-and-play: Python dependencies are vendored, no `pip install` needed
- Auto-installs Nmap if missing (requires `sudo`)

---

## Requirements

- Raspberry Pi (or Linux with Python 3.11+)
- Internet access for Nmap installation (only if Nmap is not already installed)

---

## Usage

1. Clone the repository:

```bash
git clone https://github.com/JacekKac/AFE-firmware-tools.git
cd AFE-firmware-tools


2. Run

To run the AFE script:

Automatically detect the subnet to scan:

python3 -m afe.afe


Override the automatically detected subnet:

python3 -m afe.afe --ip <subnet_ip>


Example:

python3 -m afe.afe --ip 192.168.0.1


You can also upgrade the firmware using a .bin file located inside the afe folder.

Firmware Notice

There is no direct download link to the AFE firmware on Adrian’s website.
To obtain it, inspect the network requests using your browser’s developer tools (F12), locate the firmware URL, and download it using wget:

wget -O AFE-Firmware.zip "https://drive.usercontent.google.com/download?id=1uchrw-7uKOXyqqyRF4vv0EANoy5rGRuY&export=download&authuser=0"


After downloading, extract the correct .bin file into the AFE/afe directory.