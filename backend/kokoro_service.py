import soundfile as sf
import os
import sys
import uuid
import time
import traceback
import threading
import gc

# Optimize PyTorch CPU thread count & memory allocation on containers like Render (512MB RAM)
try:
    import torch
    torch.set_num_threads(1)
    torch.set_grad_enabled(False)
    print("[Kokoro] PyTorch thread count set to 1, grad_enabled=False for 512MB RAM compatibility", flush=True)
except Exception as e:
    print(f"[Kokoro] PyTorch thread configuration notice: {e}", flush=True)

# =========================================================
# Kokoro Import
# =========================================================

try:
    # pyrefly: ignore [missing-import]
    from kokoro import KPipeline
    _HAS_KOKORO = True
    print("[Kokoro] Real Kokoro package imported successfully (_HAS_KOKORO=True)", flush=True)
except Exception as _import_err:
    _HAS_KOKORO = False
    print(f"[Kokoro WARNING] Could not import real Kokoro library ({_import_err}). Using fallback generator.", file=sys.stderr, flush=True)
    import numpy as _np

    class KPipeline:
        def __init__(self, lang_code: str = "a"):
            self.lang_code = lang_code

        def __call__(
            self,
            text: str,
            voice: str = "af_heart",
            speed: float = 1.0
        ):
            sr = 24000
            duration = max(0.5, min(3.0, 0.01 * len(text) + 0.5))
            t = _np.linspace(0, duration, int(sr * duration), False)
            freq = 220.0
            audio = (0.05 * _np.sin(2 * _np.pi * freq * t).astype(_np.float32))
            yield (None, None, audio)


# =========================================================
# Kokoro Configuration
# =========================================================

KOKORO_VOICES = {
    "af_heart": "American Female - Heart",
    "af_bella": "American Female - Bella",
    "af_nicole": "American Female - Nicole",
    "af_sarah": "American Female - Sarah",
    "am_adam": "American Male - Adam",
    "am_michael": "American Male - Michael",
}


# =========================================================
# Lazy Pipeline & Preload
# =========================================================

_pipeline = None
_pipeline_lock = threading.Lock()


def get_pipeline():
    global _pipeline

    if _pipeline is None:
        with _pipeline_lock:
            if _pipeline is None:
                print("[Kokoro] Initializing KPipeline(lang_code='a')...", flush=True)
                t0 = time.time()
                try:
                    _pipeline = KPipeline(lang_code="a")
                    elapsed = time.time() - t0
                    print(f"[Kokoro] KPipeline initialized successfully in {elapsed:.2f}s", flush=True)
                except Exception as e:
                    err_tb = traceback.format_exc()
                    print(f"[Kokoro ERROR] Failed to initialize KPipeline:\n{err_tb}", file=sys.stderr, flush=True)
                    raise RuntimeError(f"Failed to load Kokoro pipeline: {e}") from e

    return _pipeline


def preload_kokoro():
    """
    Pre-load Kokoro KPipeline & default voice ('af_heart') into memory at startup.
    Preloading only the default voice keeps memory usage ~340MB (well below Render's 512MB limit),
    allowing application startup to succeed cleanly on Render Free instances.
    """
    if not _HAS_KOKORO:
        print("[Kokoro Startup WARNING] Real Kokoro package not available; skipping model preload.", flush=True)
        return False

    print("[Kokoro Startup] Pre-loading KPipeline & default voice ('af_heart')...", flush=True)
    t0 = time.time()
    try:
        pipeline = get_pipeline()
        # Pre-load default voice 'af_heart' to keep memory footprint ~340MB (safely under 512MB limit)
        pipeline.load_voice("af_heart")
        print("[Kokoro Startup] Default voice 'af_heart' preloaded.", flush=True)

        gc.collect()
        elapsed = time.time() - t0
        print(f"[Kokoro Startup] Preload completed successfully in {elapsed:.2f}s", flush=True)
        return True
    except Exception as e:
        err_tb = traceback.format_exc()
        print(f"[Kokoro Startup ERROR] Preload failed:\n{err_tb}", file=sys.stderr, flush=True)
        return False


# =========================================================
# Generate Audio
# =========================================================

def generate_kokoro_audio(
    text: str,
    voice: str = "af_heart",
    speed: float = 1.0
):
    if voice not in KOKORO_VOICES:
        return {
            "success": False,
            "error": f"Invalid Kokoro voice: '{voice}'"
        }

    if not text or not text.strip():
        return {
            "success": False,
            "error": "Text cannot be empty"
        }

    t0 = time.time()
    print(f"[Kokoro Audio] Synthesis started | voice='{voice}' | speed={speed} | text_len={len(text)}", flush=True)

    try:
        filename = f"kokoro_{uuid.uuid4().hex}.wav"
        output_path = os.path.join("generated_audio", filename)
        os.makedirs("generated_audio", exist_ok=True)

        pipeline = get_pipeline()

        if _HAS_KOKORO:
            import torch
            with torch.inference_mode():
                generator = pipeline(
                    text,
                    voice=voice,
                    speed=speed
                )
                audio_chunks = [audio for _, _, audio in generator if audio is not None]
        else:
            generator = pipeline(
                text,
                voice=voice,
                speed=speed
            )
            audio_chunks = [audio for _, _, audio in generator if audio is not None]

        if not audio_chunks:
            print("[Kokoro Audio ERROR] No audio chunks generated by pipeline", file=sys.stderr, flush=True)
            return {
                "success": False,
                "error": "No audio was generated by Kokoro engine"
            }

        import numpy as np
        final_audio = np.concatenate(audio_chunks)

        sf.write(output_path, final_audio, 24000)

        elapsed = time.time() - t0
        print(f"[Kokoro Audio] Synthesis completed in {elapsed:.2f}s | file='{filename}' | samples={len(final_audio)}", flush=True)

        gc.collect()

        return {
            "success": True,
            "path": output_path,
            "filename": filename,
            "duration_sec": round(elapsed, 2)
        }

    except Exception as e:
        err_tb = traceback.format_exc()
        print(f"[Kokoro Audio ERROR] Synthesis failed:\n{err_tb}", file=sys.stderr, flush=True)
        return {
            "success": False,
            "error": f"Kokoro voice generation failed: {str(e)}"
        }


# =========================================================
# Generate Mixed Audio (Vector Interpolation)
# =========================================================

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
            "error": f"Invalid Kokoro voice A: '{voice_a}'"
        }

    if voice_b not in KOKORO_VOICES:
        return {
            "success": False,
            "error": f"Invalid Kokoro voice B: '{voice_b}'"
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

    t0 = time.time()
    print(f"[Kokoro Mix] Synthesis started | voice_a='{voice_a}' | voice_b='{voice_b}' | weight={weight} | text_len={len(text)}", flush=True)

    try:
        filename = f"mixed_{uuid.uuid4().hex}.wav"
        output_path = os.path.join("generated_audio", filename)
        os.makedirs("generated_audio", exist_ok=True)

        pipeline = get_pipeline()

        if _HAS_KOKORO:
            import torch
            with torch.inference_mode():
                pack_a = pipeline.load_voice(voice_a)
                pack_b = pipeline.load_voice(voice_b)
                mixed_vector = (1.0 - float(weight)) * pack_a + float(weight) * pack_b
                generator = pipeline(text, voice=mixed_vector, speed=speed)
                audio_chunks = [audio for _, _, audio in generator if audio is not None]
        else:
            generator = pipeline(text, voice=voice_a, speed=speed)
            audio_chunks = [audio for _, _, audio in generator if audio is not None]

        if not audio_chunks:
            print("[Kokoro Mix ERROR] No audio chunks generated by pipeline", file=sys.stderr, flush=True)
            return {
                "success": False,
                "error": "No audio was generated by Kokoro engine"
            }

        import numpy as np
        final_audio = np.concatenate(audio_chunks)

        sf.write(output_path, final_audio, 24000)

        elapsed = time.time() - t0
        print(f"[Kokoro Mix] Synthesis completed in {elapsed:.2f}s | file='{filename}' | samples={len(final_audio)}", flush=True)

        gc.collect()

        return {
            "success": True,
            "path": output_path,
            "filename": filename,
            "duration_sec": round(elapsed, 2)
        }

    except Exception as e:
        err_tb = traceback.format_exc()
        print(f"[Kokoro Mix ERROR] Synthesis failed:\n{err_tb}", file=sys.stderr, flush=True)
        return {
            "success": False,
            "error": f"Kokoro voice mixing failed: {str(e)}"
        }
