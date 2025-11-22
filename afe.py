import xml.etree.ElementTree as ET
import subprocess
import requests
from bs4 import BeautifulSoup
import socket

# ------------------------------------------------------
# GET LOCAL IP + GENERATE SCAN RANGE
# ------------------------------------------------------
def get_local_subnet_range():
    try:
        # Detect primary local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # doesn't send data; safe
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        # fallback
        local_ip = socket.gethostbyname(socket.gethostname())

    parts = local_ip.split(".")
    subnet = ".".join(parts[:3])
    scan_range = f"{subnet}.1-254"

    print(f"[INFO] Local IP detected: {local_ip}")
    print(f"[INFO] Scanning subnet range: {scan_range}")

    return scan_range


# ------------------------------------------------------
# NMAP SCAN
# ------------------------------------------------------
def run_nmap_scan(target):
    command = f'nmap -oX - -p80 --open {target}'
    print("\n[INFO] Searching for AFE Firmware devices...\n")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stde                                                                                                                                                             rr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode()


# ------------------------------------------------------
# PARSE NMAP OUTPUT
# ------------------------------------------------------
def parse_nmap_xml(xml_content):
    root = ET.fromstring(xml_content)
    host_info = []

    for host in root.findall('.//host'):
        address_elem = host.find('.//address[@addrtype="ipv4"]')
        hostname_elem = host.find('.//hostname')

        if address_elem is not None:
            ip = address_elem.attrib['addr']
            hostname = hostname_elem.attrib.get('name', '') if hostname_elem is                                                                                                                                                              not None else ''
            host_info.append((ip, hostname))

    return host_info


# ------------------------------------------------------
# EXTRACT INFO FROM AFE HTML PAGE
# ------------------------------------------------------
def extract_afe_info(html):
    soup = BeautifulSoup(html, 'html.parser')

    info = {
        "title": None,
        "device": None,
        "version": None,
        "ram": None
    }

    # Title (e.g. "AFE Firmware")
    h1s = soup.find_all('h1')
    if h1s:
        info['title'] = h1s[0].text.strip()

    # Device (e.g. "ESP1")
    for h1 in h1s:
        if 'Urządzenie' in h1.text:
            info['device'] = h1.text.replace('Urządzenie:', '').strip()

    # Version + RAM (in <small>)
    small = soup.find('small')
    if small:
        text = small.text
        if 'Wersja' in text:
            info['version'] = text.split('Wersja')[1].split('(')[0].strip(': ')
        if 'RAM' in text:
            info['ram'] = text.split('RAM')[1].strip()

    return info


# ------------------------------------------------------
# CHECK DEVICE FOR AFE FIRMWARE + GATHER INFO
# ------------------------------------------------------
def check_for_afe(ip, hostname):
    url = f'http://{ip}'
    try:
        response = requests.get(url, timeout=5)
        if "AFE" in response.text:
            info = extract_afe_info(response.text)
            print(f"FOUND AFE DEVICE: {ip} ({hostname})")
            print(f"  • Title:   {info['title']}")
            print(f"  • Device:  {info['device']}")
            print(f"  • Version: {info['version']}")
            print(f"  • RAM:     {info['ram']}\n")
    except requests.exceptions.RequestException:
        pass


# ------------------------------------------------------
# MAIN
# ------------------------------------------------------
if __name__ == "__main__":
    target = get_local_subnet_range()
    nmap_output = run_nmap_scan(target)
    host_info = parse_nmap_xml(nmap_output)

    for ip, hostname in host_info:
        check_for_afe(ip, hostname)
