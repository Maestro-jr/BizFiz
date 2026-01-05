#!/usr/bin/env python3

import subprocess
import sys
import time
import signal
from pathlib import Path
import socket

BASE_DIR = Path(__file__).parent

DFS_SERVERS = [
    ("DFS1", "dfs1.py", 10001),
    ("DFS2", "dfs2.py", 10002),
    ("DFS3", "dfs3.py", 10003),
    ("DFS4", "dfs4.py", 10004),
]

processes = []


def wait_for_server(port, host="127.0.0.1", timeout=10):
    """Wait until a server is listening on host:port"""
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except (ConnectionRefusedError, socket.timeout):
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.2)


def start_servers():
    print("[+] Starting DFS servers...")
    for folder, script, port in DFS_SERVERS:
        server_dir = BASE_DIR / folder
        p = subprocess.Popen(
            [sys.executable, script, str(port)],
            cwd=server_dir
        )
        processes.append(p)
        print(f"    - {folder}/{script} on port {port}")

    # Wait for each server to be ready
    for folder, _, port in DFS_SERVERS:
        if wait_for_server(port):
            print(f"[✓] {folder} is ready on port {port}")
        else:
            print(f"[!] {folder} failed to start on port {port}")


def start_client():
    print("\n[+] Starting DFC client...\n")
    subprocess.call(
        [sys.executable, "dfc.py", "dfc.conf"],
        cwd=BASE_DIR / "DFC"
    )


def shutdown(signum=None, frame=None):
    print("\n[!] Shutting down DFS cluster...")
    for p in processes:
        p.terminate()
        p.wait()
    print("[✓] All servers stopped")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, shutdown)
    start_servers()
    start_client()
    shutdown()


if __name__ == "__main__":
    main()
