from pymongo import MongoClient
from dotenv import load_dotenv
import os

# =========================
# Load Environment Variables
# =========================

load_dotenv()

# =========================
# MongoDB Connection
# =========================

MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)

db = client["audioflow"]

users_collection = db["users"]

audios_collection = db["audios"]

print("✅ MongoDB Connected Successfully")