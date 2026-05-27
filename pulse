import socket
import time
import argparse
import asyncio
from colorama import Fore, Style, init

init(autoreset=True)

parser = argparse.ArgumentParser(
    description="Async port Scanner with verbosity control"
)

parser.add_argument("host")
parser.add_argument("ports")
parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    default=0,
    help="Increase verbosity by pressing(-v, -vv, -vvv)",
)

args = parser.parse_args()

host = args.host
port_range = args.ports

open_ports = []
queue = asyncio.Queue()

verbose = args.verbose


def log(msg, level=1, color=Fore.WHITE):
    if verbose >= level:
        print(color + msg + Style.RESET_ALL)


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


semaphore = asyncio.Semaphore(5000)


async def scan_port(ip, port):
    try:
        async with semaphore:

            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(ip, port), timeout=1
            )

            writer.close()

            await writer.wait_closed()
            return port

    except asyncio.TimeoutError:
        log(f"Debug: timeout at port{port}", level=3, color=Fore.RED)
    except ConnectionRefusedError:
        return None
    except OSError:
        return None


async def Producer():
    for port in range(start_port, end_port + 1):
        await queue.put(port)


async def Worker(ip):
    while True:
        port = await queue.get()

        if port is None:
            queue.task_done()
            break

        result = await scan_port(ip, port)
        if result is not None:
            log(f"Trying Port{port}", level=2, color=Fore.LIGHTCYAN_EX)
            open_ports.append(result)

        queue.task_done()


async def main():
    ip = host_resolver(host)
    log(
        f"Starting scan on {host} ports {start_port} - {end_port}",
        level=1,
        color=Fore.CYAN,
    )

    if ip is None:
        return
    start_time = time.time()

    await Producer()
    workers = []
    worker_count = 1000
    for work in range(worker_count):
        workers.append(asyncio.create_task(Worker(ip)))

    await queue.join()
    for work in range(worker_count):
        await queue.put(None)
    await asyncio.gather(*workers)
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
