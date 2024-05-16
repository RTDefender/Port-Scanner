import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((ip, port))
        banner = s.recv(1024).decode().strip()
        return banner
    except:
        return "No banner"

# Function to scan a single port
def port_scanner(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((ip, port))
        s.close()
        banner = grab_banner(ip, port)
        return (port, "open", banner)
    except:
        return (port, "closed", None)

# Main function to manage the scanning process
def main():
    # User input for target IP address
    target = input("Enter the target IP address to scan: ")

    if not is_valid_ip(target):
        print("Invalid IP address.")
        return

    # User input for port range
    print("Enter the range of ports to scan (format: start-end):")
    start_port, end_port = map(int, input().split('-'))

    # Capture start time
    start_time = datetime.now()
    print(f"Scanning started at: {start_time}")

    # Using ThreadPoolExecutor to limit the number of concurrent threads
    max_workers = 100  # Adjust this based on your system's capabilities
    open_ports = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {executor.submit(port_scanner, target, port): port for port in range(start_port, end_port + 1)}
        for future in future_to_port:
            port, status, banner = future.result()
            if status == "open":
                print(f"Port {port} is open")
                if banner:
                    print(f"Banner: {banner}")
                open_ports.append(port)

    # Capture end time
    end_time = datetime.now()
    print(f"Scanning completed at: {end_time}")
    duration = end_time - start_time
    print(f"Total scanning duration: {duration}")

if __name__ == "__main__":
    main()
