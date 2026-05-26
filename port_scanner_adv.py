import socket
import time
import argparse
import asyncio

parser = argparse.ArgumentParser()

parser.add_argument("host")
parser.add_argument("ports")

args = parser.parse_args()

host = args.host
port_range = args.ports


def host_resolver(host):

    try:
        return socket.gethostbyname(host)

    except socket.gaierror:
        print("Invalid or Unknown Hostname.")
        return None


try:

    start_port, end_port = port_range.split("-")

    start_port = int(start_port)
    end_port = int(end_port)

    if start_port < 0 or end_port > 65535:
        print("Ports must be between 0 and 65535.")
        exit()

    if start_port > end_port:
        print("Invalid Port Range.")
        exit()

except ValueError:
    print("Invalid Port Range Format.")
    exit()


async def scan_port(ip, port):

    try:

        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), timeout=1
        )

        writer.close()

        await writer.wait_closed()

        return port

    except:
        return None


async def main():

    ip = host_resolver(host)

    if ip is None:
        return

    start_time = time.time()

    tasks = []

    for port in range(start_port, end_port + 1):

        tasks.append(scan_port(ip, port))

    results = await asyncio.gather(*tasks)

    open_ports = [port for port in results if port is not None]

    end_time = time.time()

    scan_time = round(end_time - start_time, 2)

    print("\nTarget Information")
    print("-" * 20)

    print(f"Resolved IP: {ip}")

    print("\nResults")
    print("-" * 20)

    for port in open_ports:

        print(f"[+] Port {port} is open")

    print("\nSummary")
    print("-" * 20)

    print(f"Open Ports Found: {len(open_ports)}")
    print(f"Scan Completed In {scan_time} sec")


asyncio.run(main())
