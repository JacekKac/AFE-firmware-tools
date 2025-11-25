#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import socket
import argparse

# Dodanie folderu vendor do sys.path (do pakietów w katalogu lokalnym)
current_dir = os.path.dirname(os.path.abspath(__file__))
vendor_dir = os.path.join(current_dir, "vendor")
sys.path.insert(0, vendor_dir)

import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

# ------------------------------------------------------
# ARGUMENTY
# ------------------------------------------------------
parser = argparse.ArgumentParser(description="AFE Firmware Scanner and Updater")
parser.add_argument(
    "--ip",
    type=str,
    help="Podaj ręcznie adres IP lub zakres sieci (np. 192.168.0.1) do nadpisania automatycznego wykrywania"
)
args = parser.parse_args()

# ------------------------------------------------------
# SPRAWDZENIE NMAP
# ------------------------------------------------------
if shutil.which("nmap") is None:
    print("[INFO] Nmap nie jest zainstalowany. Instaluję...")
    try:
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        subprocess.run(["sudo", "apt-get", "install", "-y", "nmap"], check=True)
        print("[INFO] Nmap zainstalowany.")
    except subprocess.CalledProcessError:
        print("[ERROR] Nie udało się zainstalować Nmap. Zainstaluj ręcznie:")
        print("  sudo apt update && sudo apt install nmap")
        sys.exit(1)

# ------------------------------------------------------
# FUNKCJE
# ------------------------------------------------------
def get_local_subnet_range():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = socket.gethostbyname(socket.gethostname())

    parts = local_ip.split(".")
    subnet = ".".join(parts[:3])
    scan_range = f"{subnet}.1-254"

    print(f"[INFO] Local IP detected: {local_ip}")
    print(f"[INFO] Scanning subnet range: {scan_range}")
    return scan_range

def run_nmap_scan(target):
    command = f"nmap -oX - -p80 --open {target}"
    print("\n[INFO] Szukam urządzeń AFE...\n")
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = process.communicate()
    return output.decode()

def parse_nmap_xml(xml_content):
    host_info = []
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        return host_info

    for host in root.findall('.//host'):
        address_elem = host.find('.//address[@addrtype="ipv4"]')
        hostname_elem = host.find('.//hostname')
        if address_elem is not None:
            ip = address_elem.attrib['addr']
            hostname = hostname_elem.attrib.get('name', '') if hostname_elem is not None else ''
            host_info.append((ip, hostname))
    return host_info

def extract_afe_info(html):
    soup = BeautifulSoup(html, 'html.parser')
    info = {"title": None, "device": None, "version": None, "ram": None}
    h1s = soup.find_all('h1')
    if h1s:
        info['title'] = h1s[0].text.strip()
    for h1 in h1s:
        if 'Urządzenie' in h1.text:
            info['device'] = h1.text.replace('Urządzenie:', '').strip()
    small = soup.find('small')
    if small:
        text = small.text
        if 'Wersja' in text:
            info['version'] = text.split('Wersja')[1].split('(')[0].strip(': ')
        if 'RAM' in text:
            info['ram'] = text.split('RAM')[1].strip()
    return info

def check_for_afe(ip, hostname):
    url = f"http://{ip}"
    try:
        response = requests.get(url, timeout=5)
        if "AFE" in response.text:
            info = extract_afe_info(response.text)
            print(f"FOUND AFE DEVICE: {ip} ({hostname})")
            print(f"  • Title:   {info['title']}")
            print(f"  • Device:  {info['device']}")
            print(f"  • Version: {info['version']}")
            print(f"  • RAM:     {info['ram']}\n")
            return (ip, info['title'] or hostname)
    except requests.exceptions.RequestException:
        pass
    return None

# ------------------------------------------------------
# FUNKCJA AKTUALIZACJI FIRMWARE
# ------------------------------------------------------
def update_firmware(ip, firmware_path):
    import os, requests

    if not os.path.exists(firmware_path):
        print(f"[ERROR] Plik firmware nie istnieje: {firmware_path}")
        return

    url = f"http://{ip}/upgrade?o=21"
    files = {"update": open(firmware_path, "rb")}  # dokładnie pole 'update' z formularza

    print(f"[INFO] Wysyłam firmware do {ip}... (to może potrwać kilkadziesiąt sekund)")
    try:
        response = requests.post(url, files=files, timeout=180)  # timeout 3 minuty
        if response.status_code == 200:
            print("[INFO] Plik przesłany, ESP powinno się zrestartować.")
        else:
            print(f"[WARN] Otrzymano kod HTTP {response.status_code}, ale ESP może się i tak zaktualizować")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Błąd połączenia: {e}")
    finally:
        files['update'].close()

def firmware_update_menu(devices):
    if not devices:
        return
    print("\n[INFO] Dostępne płytki do aktualizacji firmware:\n")
    for idx, (ip, name) in enumerate(devices, 1):
        print(f"{idx}. Aktualizacja firmware płytki \"{name}\" - {ip}")

    choice = input("\nWybierz numer płytki do aktualizacji (0 aby pominąć): ")
    if not choice.isdigit():
        print("[ERROR] Niepoprawny wybór!")
        return
    choice = int(choice)
    if choice == 0:
        return
    if 1 <= choice <= len(devices):
        selected_ip, selected_name = devices[choice - 1]
        confirm = input(f"Czy na pewno chcesz zaktualizować firmware płytki \"{selected_name}\" ({selected_ip})? [y/n]: ")
        if confirm.lower() != 'y':
            print("[INFO] Aktualizacja anulowana.")
            return

        firmware_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        bin_files = [f for f in os.listdir(firmware_dir) if f.endswith('.bin')]

        if bin_files:
            print("\n[INFO] Dostępne pliki firmware:")
            for idx, fname in enumerate(bin_files, 1):
                print(f"{idx}. {fname}")
            file_choice = input("\nWybierz numer pliku firmware do wysłania: ")
            if not file_choice.isdigit():
                print("[ERROR] Niepoprawny wybór!")
                return
            file_choice = int(file_choice)
            if 1 <= file_choice <= len(bin_files):
                firmware_path = os.path.join(firmware_dir, bin_files[file_choice - 1])
            else:
                print("[ERROR] Niepoprawny numer pliku firmware.")
                return
        else:
            firmware_path = input("Brak plików .bin w katalogu skryptu. Podaj pełną ścieżkę do pliku firmware: ")
            if not os.path.exists(firmware_path):
                print(f"[ERROR] Plik firmware nie istnieje: {firmware_path}")
                return

        update_firmware(selected_ip, firmware_path)
    else:
        print("[ERROR] Nieprawidłowy numer płytki.")

# ------------------------------------------------------
# MAIN
# ------------------------------------------------------
if __name__ == "__main__":
    if args.ip:
        target = args.ip
        print(f"[INFO] Nadpisano adres IP/range na: {target}")
    else:
        target = get_local_subnet_range()

    nmap_output = run_nmap_scan(target)
    raw_devices = parse_nmap_xml(nmap_output)

    # Tylko faktyczne AFE devices
    afe_devices = []
    for ip, hostname in raw_devices:
        dev = check_for_afe(ip, hostname)
        if dev:
            afe_devices.append(dev)

    firmware_update_menu(afe_devices)
