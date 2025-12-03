import secrets
from .encryption import generate_key, encrypt_text

def generate_secure_password(length=16):
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def create_master_credentials(key_path, enc_path):
    key = generate_key()
    with open(key_path, "wb") as f:
        f.write(key)

    password = generate_secure_password()
    encrypted = encrypt_text(password, key)

    with open(enc_path, "wb") as f:
        f.write(encrypted)

    return password
