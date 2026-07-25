from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Header,
    HTTPException,
    Depends
)

from pydantic import BaseModel

from database import (
    users_collection,
    audios_collection
)

from cloudinary_service import upload_audio

from auth import (
    hash_password,
    verify_password,
    validate_password,
    create_token,
    verify_token
)

from email_validator import (
    validate_email,
    EmailNotValidError
)

from datetime import datetime

import os
import shutil



app = FastAPI()



UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)




# =========================
# Models
# =========================

class RegisterUser(BaseModel):

    name: str
    email: str
    password: str



class LoginUser(BaseModel):

    email: str
    password: str





# =========================
# JWT Authentication
# =========================

async def get_current_user(
    authorization: str = Header(None)
):

    if not authorization:

        raise HTTPException(
            status_code=401,
            detail="Authorization token missing"
        )



    token = authorization.replace(
        "Bearer ",
        ""
    )



    email = verify_token(token)



    if not email:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )



    return email





# =========================
# Root
# =========================

@app.get("/")
async def root():

    return {
        "message": "Audio Transfer API Running"
    }





# =========================
# Register
# =========================

@app.post("/register")
async def register(
    user: RegisterUser
):


    # Email validation

    try:

        email_info = validate_email(
            user.email,
            check_deliverability=False
        )

        user.email = email_info.normalized



    except EmailNotValidError:


        return {

            "success": False,

            "message": "Invalid email address"

        }




    # Password validation

    valid, message = validate_password(
        user.password
    )



    if not valid:

        return {

            "success": False,

            "message": message

        }





    # Check existing user

    existing_user = users_collection.find_one(
        {
            "email": user.email
        }
    )



    if existing_user:


        return {

            "success": False,

            "message": "Email already registered"

        }




    # Hash password

    hashed_password = hash_password(
        user.password
    )




    users_collection.insert_one({

        "name": user.name,

        "email": user.email,

        "password": hashed_password

    })



    return {

        "success": True,

        "message": "Registration Successful"

    }





# =========================
# Login
# =========================

@app.post("/login")
async def login(
    user: LoginUser
):


    existing_user = users_collection.find_one(
        {
            "email": user.email
        }
    )



    if not existing_user:


        return {

            "success": False,

            "message": "Invalid Email or Password"

        }




    password_match = verify_password(

        user.password,

        existing_user["password"]

    )



    if not password_match:


        return {

            "success": False,

            "message": "Invalid Email or Password"

        }




    token = create_token(
        existing_user["email"]
    )




    return {

        "success": True,

        "message": "Login Successful",

        "access_token": token,

        "user": {

            "name": existing_user["name"],

            "email": existing_user["email"]

        }

    }





# =========================
# Upload Audio Protected
# =========================

@app.post("/receive")
async def receive_file(

    file: UploadFile = File(...),

    user_email: str = Depends(get_current_user)

):


    file_path = os.path.join(

        UPLOAD_DIR,

        file.filename

    )



    with open(
        file_path,
        "wb"
    ) as buffer:


        shutil.copyfileobj(

            file.file,

            buffer

        )





    result = upload_audio(
        file_path
    )





    if os.path.exists(file_path):

        os.remove(file_path)





    if not result["success"]:


        return {

            "success": False,

            "message": result["error"]

        }





    audios_collection.insert_one({

        "filename": file.filename,

        "url": result["url"],

        "public_id": result["public_id"],

        "uploaded_by": user_email,

        "uploaded_at": datetime.utcnow()

    })





    return {

        "success": True,

        "message": "Audio uploaded successfully",

        "url": result["url"]

    }





# =========================
# Fetch User Audios
# =========================

@app.get("/audios")
async def get_audios(

    user_email: str = Depends(get_current_user)

):


    audios = []



    for audio in audios_collection.find(
        {
            "uploaded_by": user_email
        }
    ):


        audios.append({

            "filename": audio["filename"],

            "url": audio["url"]

        })



    return {

        "success": True,

        "count": len(audios),

        "audios": audios

    }