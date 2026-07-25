import cloudinary.uploader
from cloudinary_config import *

def upload_audio(file_path):
    try:
        result = cloudinary.uploader.upload(
            file_path,
            resource_type="video"   # Audio files Cloudinary mein "video" resource type ke under store hote hain
        )

        return {
            "success": True,
            "url": result["secure_url"],
            "public_id": result["public_id"]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }