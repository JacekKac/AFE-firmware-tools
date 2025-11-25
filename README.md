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

python3 -m afe.afe