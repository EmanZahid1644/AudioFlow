from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    Depends
)

from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
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

from kokoro_service import (
    generate_kokoro_audio,
    generate_kokoro_mixed_audio,
    preload_kokoro,
    KOKORO_VOICES
)

from datetime import datetime

import shutil
import tempfile
import os
import time
import uuid
from starlette.concurrency import run_in_threadpool

# =========================================================
# FastAPI App
# =========================================================

app = FastAPI(
    title="AudioFlow API",
    version="0.1.0"
)


@app.on_event("startup")
async def startup_event():
    print("[Application Startup] AudioFlow FastAPI server online. Kokoro TTS lazy-loaded on demand with single-thread RAM optimization.", flush=True)


# =========================================================
# JWT / Swagger Authentication
# =========================================================

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get the currently authenticated user from JWT token.
    Swagger will automatically show the Authorize button.
    """

    token = credentials.credentials

    email = verify_token(token)

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return email


# =========================================================
# Models
# =========================================================

class RegisterUser(BaseModel):

    name: str
    email: str
    password: str


class LoginUser(BaseModel):

    email: str
    password: str


class VoiceGenerationRequest(BaseModel):

    text: str
    voice: str = "af_heart"
    speed: float = 1.0


class VoiceMixRequest(BaseModel):

    text: str
    voice_a: str | None = None
    voice_b: str | None = None
    voice_1: str | None = None
    voice_2: str | None = None
    weight: float = 0.5
    speed: float = 1.0



class CloneGenerateRequest(BaseModel):

    sample_id: str
    text: str


# =========================================================
# Root
# =========================================================

@app.get("/")
async def root():

    return {
        "message": "Audio Transfer API Running"
    }


# =========================================================
# Register
# =========================================================

@app.post("/register")
async def register(
    user: RegisterUser
):

    # -----------------------------------------------------
    # Validate Email
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Validate Password
    # -----------------------------------------------------

    valid, message = validate_password(
        user.password
    )

    if not valid:

        return {
            "success": False,
            "message": message
        }


    # -----------------------------------------------------
    # Check Existing User
    # -----------------------------------------------------

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


    # -----------------------------------------------------
    # Hash Password
    # -----------------------------------------------------

    hashed_password = hash_password(
        user.password
    )


    # -----------------------------------------------------
    # Save User
    # -----------------------------------------------------

    users_collection.insert_one({

        "name": user.name,

        "email": user.email,

        "password": hashed_password,

        "created_at": datetime.utcnow()

    })


    return {

        "success": True,

        "message": "Registration Successful"

    }


# =========================================================
# Login
# =========================================================

@app.post("/login")
async def login(
    user: LoginUser
):

    def _log(msg: str):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'login_debug.log'), 'a', encoding='utf8') as fh:
                fh.write(msg + "\n")
        except Exception:
            pass

    _log(f"LOGIN: request for {user.email}")
    # -----------------------------------------------------
    # Find User
    # -----------------------------------------------------

    t0 = time.time()
    existing_user = users_collection.find_one({"email": user.email})
    _log(f"LOGIN: db lookup elapsed {time.time()-t0:.3f}s")


    if not existing_user:

        return {

            "success": False,

            "message": "Invalid Email or Password"

        }


    # -----------------------------------------------------
    # Verify Password
    # -----------------------------------------------------
    password_match = verify_password(

        user.password,

        existing_user["password"]

    )

    _log(f"LOGIN: password verify complete")


    if not password_match:

        return {

            "success": False,

            "message": "Invalid Email or Password"

        }


    # -----------------------------------------------------
    # Create JWT
    # -----------------------------------------------------

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


# =========================================================
# LEGACY AUDIO UPLOAD / OLD CLONE ROUTES
# =========================================================

@app.post("/receive")
async def receive_file(
    file: UploadFile = File(...),
    user_email: str = Depends(get_current_user),
):
    raise HTTPException(
        status_code=410,
        detail="Deprecated. Use /clone-voice for the new voice workflow.",
    )


@app.post("/clone-generate")
async def clone_generate(
    request: CloneGenerateRequest,
    user_email: str = Depends(get_current_user),
):
    raise HTTPException(
        status_code=410,
        detail="Deprecated. Use /clone-voice for the new voice workflow.",
    )


@app.post("/clone-voice")
async def clone_voice(
    text: str = Form(...),
    reference_audio: UploadFile = File(...),
    language: str = Form("english"),
    voice_id: str | None = Form(None),
    user_email: str = Depends(get_current_user),
):
    """Generate cloned speech from text + reference audio and upload it to Cloudinary."""

    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    temp_path = None
    try:
        suffix = os.path.splitext(reference_audio.filename or "")[1] or ".wav"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(reference_audio.file, temp_file)
            temp_path = temp_file.name

        result = clone_voice_from_audio(
            reference_audio_path=temp_path,
            text=text,
            language=language,
            voice_id=voice_id,
        )

        audios_collection.insert_one({
            "filename": f"cloned_{os.path.basename(temp_path)}",
            "url": result["audio_url"],
            "public_id": result.get("public_id"),
            "uploaded_by": user_email,
            "type": "voice_cloned",
            "language": language,
            "text": text,
            "reference_fingerprint": result.get("reference_fingerprint"),
            "uploaded_at": datetime.utcnow(),
        })

        return {
            "success": True,
            "audio_url": result["audio_url"],
            "sample_rate": result.get("sample_rate"),
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# =========================================================
# FETCH USER AUDIOS
# =========================================================

@app.get("/audios")
async def get_audios(

    user_email: str = Depends(get_current_user)

):
    raise HTTPException(
        status_code=410,
        detail="Deprecated. The audio library upload/download flow has been removed.",
    )


# =========================================================
# GENERATE VOICE - KOKORO
# =========================================================

@app.post("/generate-voice")
async def generate_voice(

    request: VoiceGenerationRequest,

    user_email: str = Depends(get_current_user)

):

    # -----------------------------------------------------
    # Validate Text
    # -----------------------------------------------------

    if not request.text.strip():

        raise HTTPException(

            status_code=400,

            detail="Text cannot be empty"

        )


    # -----------------------------------------------------
    # Validate Voice
    # -----------------------------------------------------

    if request.voice not in KOKORO_VOICES:

        raise HTTPException(

            status_code=400,

            detail={
                "message": "Invalid Kokoro voice",
                "available_voices": list(
                    KOKORO_VOICES.keys()
                )
            }

        )


    # -----------------------------------------------------
    # Validate Speed
    # -----------------------------------------------------

    if request.speed <= 0:

        raise HTTPException(

            status_code=400,

            detail="Speed must be greater than 0"

        )


    # -----------------------------------------------------
    # Generate Audio Using Kokoro (Threadpool Async)
    # -----------------------------------------------------

    result = await run_in_threadpool(
        generate_kokoro_audio,
        text=request.text,
        voice=request.voice,
        speed=request.speed
    )


    if not result["success"]:

        raise HTTPException(

            status_code=500,

            detail=result["error"]

        )


    generated_path = result["path"]


    try:

        # -------------------------------------------------
        # Upload Generated Audio To Cloudinary
        # -------------------------------------------------

        cloudinary_result = upload_audio(
            generated_path
        )


        if not cloudinary_result["success"]:

            raise HTTPException(

                status_code=500,

                detail=cloudinary_result["error"]

            )


        # -------------------------------------------------
        # Save Generated Audio In MongoDB
        # -------------------------------------------------

        audio_document = {

            "filename": result["filename"],

            "url": cloudinary_result["url"],

            "public_id": cloudinary_result["public_id"],

            "uploaded_by": user_email,

            "type": "kokoro_generated",

            "model": "Kokoro-82M",

            "voice": request.voice,

            "speed": request.speed,

            "text": request.text,

            "uploaded_at": datetime.utcnow()

        }


        audios_collection.insert_one(
            audio_document
        )


        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return {

            "success": True,

            "message": "Voice generated successfully",

            "filename": result["filename"],

            "url": cloudinary_result["url"],

            "voice": request.voice,

            "speed": request.speed

        }


    finally:

        # -------------------------------------------------
        # Delete Local Generated WAV
        # -------------------------------------------------

        if os.path.exists(generated_path):

            os.remove(generated_path)


# =========================================================
# AVAILABLE KOKORO VOICES
# =========================================================

@app.get("/kokoro-voices")
async def get_kokoro_voices():

    return {

        "success": True,

        "voices": KOKORO_VOICES

    }


# =========================================================
# VOICE MIXING - KOKORO (Vector Interpolation)
# =========================================================

async def _process_voice_mix(
    request: VoiceMixRequest,
    user_email: str
):
    voice_a = request.voice_a or request.voice_1
    voice_b = request.voice_b or request.voice_2

    # 1. Validate Text
    if not request.text or not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Text cannot be empty."
        )

    if len(request.text.strip()) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Text length exceeds maximum allowed limit."
        )

    # 2. Validate Voices
    if not voice_a or voice_a not in KOKORO_VOICES:
        raise HTTPException(
            status_code=404,
            detail="Voice not found."
        )

    if not voice_b or voice_b not in KOKORO_VOICES:
        raise HTTPException(
            status_code=404,
            detail="Voice not found."
        )

    if voice_a == voice_b:
        raise HTTPException(
            status_code=400,
            detail="Voice A and Voice B must be different."
        )

    # 3. Validate Weight
    if not (0.0 <= float(request.weight) <= 1.0):
        raise HTTPException(
            status_code=400,
            detail="Weight must be between 0 and 1."
        )

    generated_path = None
    try:
        mix_res = await run_in_threadpool(
            generate_kokoro_mixed_audio,
            text=request.text,
            voice_a=voice_a,
            voice_b=voice_b,
            weight=request.weight,
            speed=request.speed
        )

        if not mix_res.get("success"):
            raise HTTPException(
                status_code=500,
                detail=mix_res.get("error", "Failed to generate mixed voice")
            )

        generated_path = mix_res["path"]

        # Upload to Cloudinary
        cloudinary_result = upload_audio(generated_path)
        if not cloudinary_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=cloudinary_result.get("error", "Cloudinary upload failed")
            )

        audio_url = cloudinary_result["url"]

        # Save metadata in MongoDB
        audio_document = {
            "filename": mix_res["filename"],
            "url": audio_url,
            "public_id": cloudinary_result.get("public_id"),
            "uploaded_by": user_email,
            "type": "voice_mixed",
            "kind": "mix",
            "model": "Kokoro-82M",
            "voice_a": voice_a,
            "voice_b": voice_b,
            "weight": request.weight,
            "text": request.text,
            "uploaded_at": datetime.utcnow()
        }

        audios_collection.insert_one(audio_document)

        return {
            "success": True,
            "message": "Mixed voice generated successfully",
            "url": audio_url,
            "audio_url": audio_url,
            "filename": mix_res["filename"],
            "kind": "mix",
            "voice_a": voice_a,
            "voice_b": voice_b,
            "weight": request.weight
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if generated_path and os.path.exists(generated_path):
            try:
                os.remove(generated_path)
            except Exception:
                pass


@app.post("/voice/mix")
async def mix_voices_endpoint(
    request: VoiceMixRequest,
    user_email: str = Depends(get_current_user),
):
    return await _process_voice_mix(request, user_email)


@app.post("/mix-voices")
async def legacy_mix_voices_endpoint(
    request: VoiceMixRequest,
    user_email: str = Depends(get_current_user),
):
    return await _process_voice_mix(request, user_email)



