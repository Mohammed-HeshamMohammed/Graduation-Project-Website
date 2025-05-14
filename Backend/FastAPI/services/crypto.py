from Crypto.Cipher import AES
import base64
import json
from app.config import SECRET_KEY

KEY = SECRET_KEY.encode()[:32]

def pad(data):
    padding = 16 - len(data) % 16
    return data + chr(padding) * padding

def unpad(data):
    padding = ord(data[-1])
    return data[:-padding]

def encrypt_json(data: dict) -> bytes:
    raw = json.dumps(data)
    cipher = AES.new(KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(raw).encode())
    return base64.b64encode(encrypted)

def decrypt_json(encrypted_data: bytes) -> dict:
    cipher = AES.new(KEY, AES.MODE_ECB)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_data)).decode()
    return json.loads(unpad(decrypted))