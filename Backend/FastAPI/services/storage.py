import os
from app.config import DATA_FILE
from app.services.crypto import encrypt_json, decrypt_json

def load_all_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "rb") as f:
        return decrypt_json(f.read())

def save_all_users(users):
    with open(DATA_FILE, "wb") as f:
        f.write(encrypt_json(users))

def load_user(email):
    users = load_all_users()
    return next((u for u in users if u["email"] == email), None)

def save_user(user):
    users = load_all_users()
    users.append(user)
    save_all_users(users)

def update_user_verified(email):
    users = load_all_users()
    for u in users:
        if u["email"] == email:
            u["verified"] = True
    save_all_users(users)