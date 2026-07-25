import cloudinary
from dotenv import load_dotenv
import os

# =========================
# Load Environment Variables
# =========================

load_dotenv()

# =========================
# Cloudinary Configuration
# =========================

cloudinary.config(

    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),

    api_key=os.getenv("CLOUDINARY_API_KEY"),

    api_secret=os.getenv("CLOUDINARY_API_SECRET"),

    secure=True

)

print("✅ Cloudinary Configured Successfully")