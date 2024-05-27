import socket
import logging
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import pyfiglet
from tqdm import tqdm
from openpyxl import Workbook
import requests

# Configure logging
logging.basicConfig(
    filename='my_port_scan_results.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Function to validate IP address
def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

# Function to grab banner from a service
def grab_banner(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            s.connect((ip, port))
            banner = s.recv(1024).decode().strip()
            return banner
    except:
        return "No banner"

# Function to get IP location
def get_ip_location(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        city = data.get("city", "Unknown")
        region = data.get("region", "Unknown")
        return city, region
    except:
        return "Unknown", "Unknown"

# Function to scan a single port
def port_scanner(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.01)
            s.connect((ip, port))
            banner = grab_banner(ip, port)
            return port, "open", banner
    except:
        return port, "closed", None

# Main function to manage the scanning process
def main():
    # Display the banner
    banner = pyfiglet.figlet_format("MY PORT SCANNER")
    print(banner)
    print("--------------------------------------------------")

    # User input for target IP address
    target = input("Enter the target IP address to scan: ")

    if not is_valid_ip(target):
        print("Invalid IP address.")
        logging.error("Invalid IP address entered: %s", target)
        return

    # Get IP location
    city, region = get_ip_location(target)

    # Capture start time in UTC
    start_time = datetime.now(timezone.utc)
    logging.info("Scanning started for target: %s at %s UTC", target, start_time)
    print(f"\nScanning Target: {target}")
    print(f"Location: {city}, {region}")
    print(f"Scanning started at: {start_time} UTC")
    print("--------------------------------------------------")

    # Using ThreadPoolExecutor to limit the number of concurrent threads
    max_workers = 1000  # Adjust this based on your system's capabilities
    open_ports = []
    total_ports = 65536

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {executor.submit(port_scanner, target, port): port for port in range(total_ports)}

        # Prepare text file
        with open('my_port_scan_results.txt', 'w') as text_file:
            text_file.write(f"Scanning Target: {target}\n")
            text_file.write(f"Location: {city}, {region}\n")
            text_file.write(f"Scanning started at: {start_time} UTC\n")
            text_file.write("--------------------------------------------------\n")

            # Prepare CSV file
            with open('my_port_scan_results.csv', mode='w', newline='') as csv_file:
                fieldnames = ['Port', 'Status', 'Banner']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()

                # Prepare Excel workbook
                wb = Workbook()
                ws = wb.active
                ws.title = "My Port Scan Results"
                ws.append(['Port', 'Status', 'Banner'])

                for future in tqdm(as_completed(future_to_port), total=total_ports, desc="Scanning Ports", unit="port"):
                    port, status, banner = future.result()
                    if status == "open":
                        print(f"Port {port} is open")
                        if banner:
                            print(f"Banner: {banner}")
                        logging.info("Port %d is open. Banner: %s", port, banner if banner else "No banner")
                        open_ports.append(port)

                        # Write results to text file
                        text_file.write(f"Port {port} is open\n")
                        if banner:
                            text_file.write(f"Banner: {banner}\n")
                        
                        # Write results to CSV file
                        writer.writerow({'Port': port, 'Status': status, 'Banner': banner if banner else "No banner"})
                        
                        # Write results to Excel file
                        ws.append([port, status, banner if banner else "No banner"])
                    else:
                        logging.debug("Port %d is closed", port)

                # Save the Excel file
                wb.save('my_port_scan_results.xlsx')

    # Capture end time in UTC
    end_time = datetime.now(timezone.utc)
    logging.info("Scanning completed at %s UTC. Total duration: %s", end_time, end_time - start_time)
    print("--------------------------------------------------")
    print(f"Scanning completed at: {end_time} UTC")
    duration = end_time - start_time
    print(f"Total scanning duration: {duration}")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()
