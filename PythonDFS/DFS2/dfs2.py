#! /usr/bin/env python3

"""
Distributed File System
Server 2
Fonyuy Berka
Jan 2026
"""

# =========================
# MODULES
# =========================
import os
import pickle
import re
import sys
import time
import socket

# =========================
# STORAGE ROOT (DFS2)
# =========================
STORAGE_ROOT = r"C:\Users\HP\Desktop\Servers\Server 2"
os.makedirs(STORAGE_ROOT, exist_ok=True)

# =========================
# ARGUMENT CHECK
# =========================
def check_args():
    if len(sys.argv) != 2:
        print("ERROR: Must supply port number \nUSAGE: py dfs2.py 10002")
        sys.exit()
    try:
        port = int(sys.argv[1])
        if port != 10002:
            print("ERROR: Port number must be 10002")
            sys.exit()
        return port
    except ValueError:
        print("ERROR: Port number must be a number.")
        sys.exit()

server_port = check_args()

# =========================
# AUTH PARAMETERS
# =========================
def auth_params():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(BASE_DIR, 'DFC', 'dfc.conf')

    if not os.path.exists(config_file):
        print(f"ERROR: {config_file} not found")
        sys.exit()

    with open(config_file, 'r', encoding='cp1252') as fh:
        users = re.findall(r'Username: .*', fh.read())

    with open(config_file, 'r', encoding='cp1252') as fh:
        passes = re.findall(r'Password: .*', fh.read())

    usernames = [u.split()[1] for u in users]
    passwords = [p.split()[1] for p in passes]

    global auth_dict
    auth_dict = dict(zip(usernames, passwords))
    return auth_dict

# =========================
# CLIENT AUTH
# =========================
def client_auth(username, password):
    if username in auth_dict and auth_dict[username] == password:
        conn.send(b"Authorization Granted.\n")
        print("Authorization Granted.")
    else:
        conn.send(b"Authorization Denied.\n")
        conn.close()
        return False
    return True

# =========================
# CREATE USER DIRECTORY
# =========================
def new_dir(username):
    user_dir = os.path.join(STORAGE_ROOT, username)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

# =========================
# PUT FILE
# =========================
def put(user_dir):
    buffersize = int(conn.recv(2048).decode())
    print("Buffer size:", buffersize)

    name1 = conn.recv(1024).decode()
    chunk1 = conn.recv(buffersize)
    file_folder = name1.split('_')[0]
    folder_path = os.path.join(user_dir, file_folder)
    os.makedirs(folder_path, exist_ok=True)
    with open(os.path.join(folder_path, name1), 'wb') as fh:
        fh.write(chunk1)
    conn.send(b"Chunk 1 transferred.\n")

    name2 = conn.recv(1024).decode()
    chunk2 = conn.recv(buffersize)
    with open(os.path.join(folder_path, name2), 'wb') as fh:
        fh.write(chunk2)
    conn.send(b"Chunk 2 transferred.\n")

# =========================
# LIST FILES
# =========================
def list_files(user_dir):
    files_list = []
    for root, _, files in os.walk(user_dir):
        files_list.extend(files)
    conn.send(pickle.dumps(files_list))

# =========================
# GET FILE
# =========================
def get(user_dir):
    filename = conn.recv(1024).decode()
    file_dir = os.path.join(user_dir, filename)
    if not os.path.isdir(file_dir):
        conn.send(b"ERROR: File not found")
        return
    chunks = os.listdir(file_dir)
    for chunk in chunks:
        chunk_path = os.path.join(file_dir, chunk)
        buffersize = os.path.getsize(chunk_path) + 4
        conn.send(str(buffersize).encode())
        time.sleep(0.2)
        conn.send(chunk.encode())
        time.sleep(0.2)
        with open(chunk_path, 'rb') as f:
            conn.send(f.read())

# =========================
# SERVER LOOP
# =========================
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", server_port))
server_socket.listen(5)
print(f"DFS2 running on port {server_port}")
print(f"Storage root: {STORAGE_ROOT}")

auth_params()

while True:
    conn, addr = server_socket.accept()
    print("Client connected from", addr)
    try:
        username = conn.recv(2048).decode()
        password = conn.recv(2048).decode()
        if not client_auth(username, password):
            continue
        user_dir = new_dir(username)
        command = conn.recv(1024).decode().lower()
        if command == "put":
            put(user_dir)
        elif command == "list":
            list_files(user_dir)
        elif command == "get":
            get(user_dir)
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()
