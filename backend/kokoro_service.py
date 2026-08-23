
import soundfile as sf
import os
import uuid

# Try to import the real Kokoro pipeline; if not available, provide a
# lightweight fallback that synthesizes a short tone so the API remains
# operational during development or on platforms without the Kokoro lib.
try:
    from kokoro import KPipeline  # type: ignore
    _HAS_KOKORO = True
except Exception:
    _HAS_KOKORO = False
    import numpy as _np

    class KPipeline:  # fallback
        def __init__(self, lang_code: str = "a"):
            self.lang_code = lang_code

        def __call__(self, text: str, voice: str = "af_heart", speed: float = 1.0):
            # Synthesize a short sine wave as a single-chunk generator
            sr = 24000
            duration = max(0.5, min(3.0, 0.01 * len(text) + 0.5))
            t = _np.linspace(0, duration, int(sr * duration), False)
            freq = 220.0
            audio = 0.05 * _np.sin(2 * _np.pi * freq * t).astype(_np.float32)
            yield (None, None, audio)


# =========================
# Kokoro Configuration
# =========================

pipeline = KPipeline(lang_code="a")


# Available Kokoro voices
KOKORO_VOICES = {
    "af_heart": "American Female - Heart",
    "af_bella": "American Female - Bella",
    "af_nicole": "American Female - Nicole",
    "af_sarah": "American Female - Sarah",
    "am_adam": "American Male - Adam",
    "am_michael": "American Male - Michael",
}


# =========================
# Generate Audio
# =========================

def generate_kokoro_audio(
    text: str,
    voice: str = "af_heart",
    speed: float = 1.0
):

    if voice not in KOKORO_VOICES:

        return {
            "success": False,
            "error": "Invalid Kokoro voice"
        }


    if not text or not text.strip():

        return {
            "success": False,
            "error": "Text cannot be empty"
        }


    try:

        filename = f"kokoro_{uuid.uuid4().hex}.wav"

        output_path = os.path.join(
            "generated_audio",
            filename
        )


        os.makedirs(
            "generated_audio",
            exist_ok=True
        )


        generator = pipeline(
            text,
            voice=voice,
            speed=speed
        )


        # Kokoro can generate multiple chunks
        audio_chunks = []

        for _, _, audio in generator:

            audio_chunks.append(audio)


        if not audio_chunks:

            return {
                "success": False,
                "error": "No audio was generated"
            }


        import numpy as np

        final_audio = np.concatenate(
            audio_chunks
        )


        sf.write(
            output_path,
            final_audio,
            24000
        )


        return {

            "success": True,

            "path": output_path,

            "filename": filename

        }


    except Exception as e:

        return {

            "success": False,

            "error": str(e)

        }


# =========================
# Generate Mixed Audio (Vector Interpolation)
# =========================

def generate_kokoro_mixed_audio(
    text: str,
    voice_a: str = "af_heart",
    voice_b: str = "am_adam",
    weight: float = 0.5,
    speed: float = 1.0
):
    if voice_a not in KOKORO_VOICES:
        return {
            "success": False,
            "error": f"Invalid Kokoro voice A: {voice_a}"
        }

    if voice_b not in KOKORO_VOICES:
        return {
            "success": False,
            "error": f"Invalid Kokoro voice B: {voice_b}"
        }

    if voice_a == voice_b:
        return {
            "success": False,
            "error": "Voice A and Voice B must be different."
        }

    if not (0.0 <= float(weight) <= 1.0):
        return {
            "success": False,
            "error": "Weight must be between 0 and 1."
        }

    if not text or not text.strip():
        return {
            "success": False,
            "error": "Text cannot be empty"
        }

    try:
        filename = f"mixed_{uuid.uuid4().hex}.wav"
        output_path = os.path.join("generated_audio", filename)
        os.makedirs("generated_audio", exist_ok=True)

        if _HAS_KOKORO:
            # Load voice vectors
            pack_a = pipeline.load_voice(voice_a)
            pack_b = pipeline.load_voice(voice_b)
            # Vector interpolation: (1 - w) * A + w * B
            mixed_vector = (1.0 - float(weight)) * pack_a + float(weight) * pack_b
            generator = pipeline(text, voice=mixed_vector, speed=speed)
        else:
            generator = pipeline(text, voice=voice_a, speed=speed)

        audio_chunks = []
        for _, _, audio in generator:
            audio_chunks.append(audio)

        if not audio_chunks:
            return {
                "success": False,
                "error": "No audio was generated"
            }

        import numpy as np
        final_audio = np.concatenate(audio_chunks)

        sf.write(output_path, final_audio, 24000)

        return {
            "success": True,
            "path": output_path,
            "filename": filename
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }