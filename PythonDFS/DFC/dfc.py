#! /usr/bin/env python3
"""
Distributed File System
Client (DFC)
Compatible with modified DFS servers
"""

import re
import os
import sys
import time
import socket
import threading
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "dfc.conf"

# ---------------- ARG CHECK ---------------- #

def check_args():
    if len(sys.argv) != 2 or sys.argv[1].lower() != 'dfc.conf':
        print("USAGE: py dfc.py dfc.conf")
        sys.exit()
    if not CONFIG_PATH.is_file():
        print(f"ERROR: {CONFIG_PATH} not found.")
        sys.exit()

# ---------------- AUTH ---------------- #

def load_auth():
    with open(CONFIG_PATH, 'r', encoding='cp1252') as fh:
        users = re.findall(r'Username: .*', fh.read())
    with open(CONFIG_PATH, 'r', encoding='cp1252') as fh:
        passes = re.findall(r'Password: .*', fh.read())
    return {u.split()[1]: p.split()[1] for u, p in zip(users, passes)}

def authenticate():
    auth = load_auth()

    for _ in range(3):
        username = input("username: ")
        if username in auth:
            break
        print("Invalid username.")
    else:
        sys.exit("Too many invalid attempts. Exiting.")

    for _ in range(3):
        password = input("password: ")
        if auth[username] == password:
            print("Authorization Granted.")
            return username, password
        print("Invalid password.")
    sys.exit("Too many invalid attempts. Exiting.")

# ---------------- SERVER CONF ---------------- #

def server_conf():
    with open(CONFIG_PATH, 'r', encoding='cp1252') as fh:
        params = re.findall(r'DFS.*', fh.read())
    servers = []
    for p in params:
        host, port = p.split()[1].split(':')
        servers.append((host, int(port)))
    return servers

# ---------------- FILE SPLIT ---------------- #

def split_file(filename, buf):
    with open(filename + '.txt', 'rb') as f:
        data = f.read()
    for i in range(4):
        with open(f"{filename}_{i+1}.txt", 'wb') as out:
            out.write(data[i*buf:(i+1)*buf])

def chunk_pairs(filename):
    pairs = [
        [f"{filename}_1.txt", f"{filename}_2.txt"],
        [f"{filename}_2.txt", f"{filename}_3.txt"],
        [f"{filename}_3.txt", f"{filename}_4.txt"],
        [f"{filename}_4.txt", f"{filename}_1.txt"]
    ]
    h = int(hashlib.md5(filename.encode()).hexdigest(), 16) % 4
    return pairs[h:] + pairs[:h]

# ---------------- GET HELPERS ---------------- #

def recv_chunks(conn, store, lock):
    try:
        bufsize = int(conn.recv(1024).decode())
        name1 = conn.recv(1024).decode()
        data1 = conn.recv(bufsize)
        with lock:
            store[name1] = data1

        conn.send(b"Transfer incomplete")

        name2 = conn.recv(1024).decode()
        data2 = conn.recv(bufsize)
        with lock:
            store[name2] = data2
    except Exception as e:
        print("Error receiving chunks:", e)

# ---------------- CLIENT ---------------- #

def client():
    username, password = authenticate()
    servers = server_conf()

    conns = []
    names = ['DFS1', 'DFS2', 'DFS3', 'DFS4']

    # Connect to DFS servers
    for i, s in enumerate(servers):
        try:
            c = socket.socket()
            c.settimeout(5)
            c.connect(s)
            c.send(username.encode())
            time.sleep(0.1)
            c.send(password.encode())
            print(f"Client connected from {names[i]}: {c.recv(1024).decode().strip()}")
            conns.append(c)
        except:
            print(f"{names[i]} unavailable")
            conns.append(None)

    command = input("Command [put|get|list]: ").lower()

    # Send command to all connected servers
    for c in conns:
        if c:
            try:
                c.send(command.encode())
            except:
                pass

    # ---------------- PUT ---------------- #
    if command == 'put':
        filename = input("Filename (no .txt): ")
        size = os.path.getsize(filename + '.txt')
        buf = size // 4 + 4

        split_file(filename, buf)
        pairs = chunk_pairs(filename)

        for i, c in enumerate(conns):
            if not c:
                continue
            try:
                c.send(str(buf).encode())
                for chunk in pairs[i]:
                    time.sleep(0.1)
                    c.send(chunk.encode())
                    time.sleep(0.1)
                    c.send(open(chunk, 'rb').read())
            except Exception as e:
                print(f"Error sending to server {i+1}:", e)

        # Clean up temp chunks
        for i in range(1, 5):
            os.remove(f"{filename}_{i}.txt")

        print("PUT completed.")

    # ---------------- GET ---------------- #
    elif command == 'get':
        filename = input("Filename: ")

        for c in conns:
            if c:
                try:
                    c.send(filename.encode())
                except:
                    pass

        store = {}
        lock = threading.Lock()
        threads = []

        for c in conns:
            if c:
                t = threading.Thread(target=recv_chunks, args=(c, store, lock))
                t.start()
                threads.append(t)

        for t in threads:
            t.join()

        if len(store) == 4:
            os.makedirs(username, exist_ok=True)
            with open(f"{username}/{filename}.txt", 'wb') as out:
                for i in range(1, 5):
                    out.write(store[f"{filename}_{i}.txt"])
            print("GET successful.")
        else:
            print("GET failed. Not all chunks received.")

    # ---------------- LIST ---------------- #
    elif command == 'list':
        for c in conns:
            if c:
                try:
                    print(c.recv(4096).decode())
                except:
                    pass

if __name__ == '__main__':
    check_args()
    client()
