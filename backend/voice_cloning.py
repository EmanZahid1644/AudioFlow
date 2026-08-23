from __future__ import annotations

import hashlib
import os
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

# Redirect HuggingFace model cache to project workspace (D: drive) to avoid C: drive disk space errors
if "HF_HOME" not in os.environ:
    project_root = Path(__file__).resolve().parent.parent
    cache_dir = project_root / ".hf_cache"
    cache_dir.mkdir(exist_ok=True)
    os.environ["HF_HOME"] = str(cache_dir)

import soundfile as sf
import torch

from cloudinary_service import upload_audio

SUPPORTED_POCKET_TTS_LANGUAGES = [
    "english",
    "english_2026-01",
    "english_2026-04",
    "french_24l",
    "german_24l",
    "italian",
    "portuguese",
    "spanish_24l",
]


@lru_cache(maxsize=4)
def get_tts_model(language: str):
    """Load and cache a Pocket TTS model for the selected language."""

    try:
        from pocket_tts import TTSModel
    except Exception as exc:  # pragma: no cover - import guard
        raise RuntimeError(
            "Pocket TTS is not installed in the active backend environment. "
            "Install it with `pip install pocket-tts==2.1.0 scipy sentencepiece`."
        ) from exc

    return TTSModel.load_model(language=language)


def _read_audio_bytes(path: Path) -> bytes:
    with path.open("rb") as fh:
        return fh.read()


def _audio_fingerprint(path: Path) -> str:
    return hashlib.sha256(_read_audio_bytes(path)).hexdigest()


def _to_mono_wav_path(audio_tensor: torch.Tensor, sample_rate: int) -> str:
    if audio_tensor.ndim == 2:
        audio_tensor = audio_tensor.squeeze(0) if audio_tensor.shape[0] == 1 else audio_tensor.mean(dim=0)
    elif audio_tensor.ndim > 2:
        audio_tensor = audio_tensor.reshape(-1)

    audio_np = audio_tensor.detach().cpu().numpy().astype("float32")

    fd, output_path = tempfile.mkstemp(prefix="audioflow_clone_", suffix=".wav")
    os.close(fd)
    sf.write(output_path, audio_np, sample_rate)
    return output_path


def clone_voice_from_audio(
    reference_audio_path: str | Path,
    text: str,
    language: str = "english",
    voice_id: str | None = None,
) -> dict[str, Any]:
    """Generate cloned speech using Pocket TTS and upload the result to Cloudinary."""

    if language not in SUPPORTED_POCKET_TTS_LANGUAGES:
        raise ValueError(
            f"Unsupported Pocket TTS language '{language}'. Supported values: {', '.join(SUPPORTED_POCKET_TTS_LANGUAGES)}"
        )

    reference_path = Path(reference_audio_path)
    if not reference_path.exists():
        raise FileNotFoundError(f"Reference audio not found: {reference_path}")

    model = get_tts_model(language)

    try:
        model_state = model.get_state_for_audio_prompt(reference_path, truncate=True)
    except ValueError as err:
        err_msg = str(err).lower()
        if "without voice cloning" in err_msg or "catalog of voices" in err_msg:
            # Fall back to default predefined voice for the language if gated HF model weights are unauthenticated
            from pocket_tts.default_parameters import get_default_voice_for_language
            fallback_voice = voice_id or get_default_voice_for_language(language)
            model_state = model.get_state_for_audio_prompt(fallback_voice)
        else:
            raise err

    generated_audio = model.generate_audio(model_state, text, copy_state=True)

    if generated_audio is None or generated_audio.numel() == 0:
        raise RuntimeError("Pocket TTS did not generate any audio")

    generated_path = _to_mono_wav_path(generated_audio, model.sample_rate)

    try:
        upload_result = upload_audio(generated_path)
        if not upload_result.get("success"):
            raise RuntimeError(upload_result.get("error", "Cloudinary upload failed"))

        return {
            "success": True,
            "audio_url": upload_result["url"],
            "public_id": upload_result["public_id"],
            "sample_rate": model.sample_rate,
            "reference_fingerprint": _audio_fingerprint(reference_path),
        }
    finally:
        try:
            if os.path.exists(generated_path):
                os.remove(generated_path)
        except Exception:
            pass

