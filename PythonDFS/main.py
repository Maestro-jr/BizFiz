#!/usr/bin/env python3

import subprocess
import sys
import time
import signal
from pathlib import Path

BASE_DIR = Path(__file__).parent

DFS_SERVERS = [
    ("DFS1", "dfs1.py", "10001"),
    ("DFS2", "dfs2.py", "10002"),
    ("DFS3", "dfs3.py", "10003"),
    ("DFS4", "dfs4.py", "10004"),
]

processes = []


def start_servers():
    print("[+] Starting DFS servers...")
    for folder, script, port in DFS_SERVERS:
        server_dir = BASE_DIR / folder
        p = subprocess.Popen(
            [sys.executable, script, port],
            cwd=server_dir
        )
        processes.append(p)
        print(f"    - {folder}/{script} on port {port}")

    time.sleep(1.5)


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
    print("[✓] All servers stopped")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, shutdown)
    start_servers()
    start_client()
    shutdown()


if __name__ == "__main__":
    main()
