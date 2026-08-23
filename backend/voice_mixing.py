import torch

def interpolate_voice_vectors(vector_a: torch.Tensor, vector_b: torch.Tensor, weight: float) -> torch.Tensor:
    """
    Interpolate two Kokoro voice style vectors using linear interpolation.
    Formula: mixed_vector = (1 - weight) * vector_a + weight * vector_b
    Where weight is between 0.0 (100% vector_a) and 1.0 (100% vector_b).
    """
    w = float(weight)
    if not (0.0 <= w <= 1.0):
        raise ValueError("Mix weight must be between 0.0 and 1.0")
    
    return (1.0 - w) * vector_a + w * vector_b
def mix_audio_files(audio_path_1: str, audio_path_2: str, output_path: str) -> bool:
    """
    Legacy audio file overlay helper.
    Note: Preferred method is neural style vector interpolation (interpolate_voice_vectors).
    """
    import soundfile as sf
    import numpy as np
    data1, sr1 = sf.read(audio_path_1, dtype="float32")
    data2, sr2 = sf.read(audio_path_2, dtype="float32")
    max_len = max(len(data1), len(data2))
    if len(data1) < max_len:
        data1 = np.pad(data1, (0, max_len - len(data1)), mode="constant")
    if len(data2) < max_len:
        data2 = np.pad(data2, (0, max_len - len(data2)), mode="constant")
    mixed = 0.5 * data1 + 0.5 * data2
    sf.write(output_path, mixed, sr1)
    return True
