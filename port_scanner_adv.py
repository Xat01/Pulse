from concurrent.futures import ThreadPoolExecutor
import socket
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("host")
parser.add_argument("ports")

args = parser.parse_args()

host = args.host
port_range = args.ports


def host_resolver(host):
    try:
        ip = socket.gethostbyname(host)
        return ip

    except socket.gaierror:
        print("Invalid or Unknown Hostname.")


try:
    start_port, end_port = port_range.split("-")

    start_port = int(start_port)
    end_port = int(end_port)

    if start_port < 0 or end_port > 65535:
        print("Ports must be between 0 and 65535.")
        exit()

    if start_port > end_port:
        print("Invalid startPort!")
        exit()

except ValueError:
    print("Invalid Port Range Format.")
    exit()


open_ports = []

common_ports = {80: "HTTP", 21: "FTP", 22: "SSH", 443: "HTTPS"}


def http_probe(sock, port):

    if port == 80:

        request = (
            "GET / HTTP/1.1\r\n" f"Host: {host}\r\n" "Connection: close\r\n" "\r\n",
            "GET / HTTPS/1.1\r\n" f"Host: {host}\r\n" "Connection: close\r\n",
        )

        request_bytes = request.encode()

        sock.sendall(request_bytes)

        response_data = b""

        try:

            while True:

                data = sock.recv(1024)

                if not data:
                    break

                response_data += data

        except socket.timeout:
            pass

        response_text = response_data.decode(errors="ignore")

        banner = response_text.split("\r\n")[0]

        return banner

    return "No HTTP Response"


def scan_port(ip, port):

    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:

            sock.settimeout(1)

            result = sock.connect_ex((ip, port))

            if result == 0:

                service = common_ports.get(port, "Unknown Service")

                banner = "No Banner"

                if port == 80:

                    banner = http_probe(sock, port)

                else:

                    try:

                        banner_data = sock.recv(1024)

                        banner = banner_data.decode(errors="ignore").strip()

                        if not banner:
                            banner = "No Banner"

                    except socket.timeout:
                        banner = "No Banner"

                open_ports.append((port, service, banner))

            else:
                return None

    except socket.error:
        pass


start_time = time.time()

ip = host_resolver(host)

if ip is not None:

    with ThreadPoolExecutor(max_workers=100) as executor:

        for port in range(start_port, end_port + 1):

            executor.submit(scan_port, ip, port)

end_time = time.time()


scan_time = round(end_time - start_time, 2)


def display_result(ip, open_ports, scan_time):

    print("Target Information:")
    print("-" * 20)

    print(f"Resolved IP: {ip}\n")

    print("Results")
    print("-" * 20)

    open_ports.sort()

    for port, service, banner in open_ports:

        print(f"[+] Port: {port} Open")
        print(f"    Service: {service}")
        print(f"    Banner: {banner}")
        print("-" * 40)

    print()

    print("Summary")
    print("-" * 20)

    print(f"Open Ports Found: {len(open_ports)}")
    print(f"Scan Completed In {scan_time} sec")


display_result(ip, open_ports, scan_time)
