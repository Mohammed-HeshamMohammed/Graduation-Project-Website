import os
from dotenv import load_dotenv

load_dotenv()

DATA_FILE = os.getenv("DATA_FILE", "app/data/.u94ks_userdata.bin")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
DOMAIN_NAME = os.getenv("DOMAIN_NAME", "http://localhost:8000")
SECRET_KEY = os.getenv("SECRET_KEY")