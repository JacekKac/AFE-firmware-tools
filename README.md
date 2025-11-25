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

## Run

Run the AFE script:

python3 -m afe.afe  - to autodect subnet to scan

python3 -m afe.afe  --ip subnet_ip to override a default detecte subnet

python3 -m afe.afe --ip 192.168.0.1


you can also upgrade firmware from .bin file iside afe folder. 



notice: there is no direct link to AFE firmware on Adrians website, you need to search for the address in developer options in your browser F12 and then use wget: 

wget -O /AFE-Firmware.zip  "https://drive.usercontent.google.com/download?id=1uchrw-7uKOXyqqyRF4vv0EANoy5rGRuY&export=download&authuser=0" unpack the RIGHT .bin file into AFE/afe folder.
