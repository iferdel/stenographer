"""Whisper via faster-whisper (CTranslate2). Default engine for the prototype.

GPU: CUDA int8_float16 if CTranslate2 sees a device (GTX 1650: ~1.5 GB VRAM for turbo, per
the research; to be confirmed). Otherwise CPU int8 (also the path on an M1 Mac; switch to an
MLX engine there later for speed). `--device mps` tries CTranslate2's experimental Metal backend.
"""

from __future__ import annotations

import ctypes
import os
import sys
import time
from pathlib import Path

from .base import Segment, Transcript, Word

DEFAULT_MODEL = "large-v3-turbo"

# Whisper copies the style of its prompt. Without a punctuated prompt, turbo often returns
# lowercase Spanish with no punctuation at all (observed on a LibriVox test clip).
STYLE_PROMPTS = {
    "es": "—¿Y usted qué opina? —preguntó ella—. Bueno, no lo sé; quizá mañana, en la estación.",
    "en": "\"And what do you think?\" she asked. \"Well, I don't know; perhaps tomorrow.\"",
}


def build_prompt(language: str, glossary: list[str]) -> str | None:
    parts = []
    if language in STYLE_PROMPTS:
        parts.append(STYLE_PROMPTS[language])
    if glossary:
        parts.append(", ".join(glossary) + ".")
    return " ".join(parts) or None


def _preload_cuda_wheels() -> None:
    """Load cuBLAS/cuDNN from the nvidia-* pip wheels so CTranslate2 finds them without a
    system CUDA install or LD_LIBRARY_PATH."""
    if sys.platform != "linux":
        return
    try:
        import nvidia.cublas
        import nvidia.cudnn
    except ImportError:
        return
    for pkg in (nvidia.cublas, nvidia.cudnn):
        for base in pkg.__path__:
            lib_dir = Path(base) / "lib"
            # cuBLASLt before cuBLAS; cuDNN's main library before its sub-libraries.
            libs = sorted(lib_dir.glob("lib*.so*"), key=lambda p: ("Lt" not in p.name, p.name))
            for lib in libs:
                try:
                    ctypes.CDLL(str(lib), mode=ctypes.RTLD_GLOBAL)
                except OSError:
                    pass


def _pick_device(device: str) -> tuple[str, str]:
    if device == "cpu":
        return "cpu", "int8"
    if device == "mps":
        # CTranslate2's Metal backend (experimental). Opt-in only: on the M1 Air it was no
        # faster than CPU int8 (5 min of audio: 56 s vs 48 s) and once crashed mid-file with
        # `IndexError: vector`. CTranslate2 runs int8 as float16 on MPS anyway.
        return "mps", "float16"
    import ctranslate2

    if ctranslate2.get_cuda_device_count() > 0:
        return "cuda", "int8_float16"
    if device == "cuda":
        raise SystemExit("CUDA requested but CTranslate2 sees no GPU.")
    return "cpu", "int8"


class WhisperEngine:
    name = "faster-whisper"

    def __init__(self, model: str = DEFAULT_MODEL, device: str = "auto",
                 compute_type: str | None = None, beam_size: int = 5):
        _preload_cuda_wheels()
        from faster_whisper import WhisperModel

        self.model_name = model
        self.device, default_ct = _pick_device(device)
        self.compute_type = compute_type or default_ct
        self.beam_size = beam_size
        cpu_threads = 0 if self.device == "cuda" else (os.cpu_count() or 4)
        self.model = WhisperModel(model, device=self.device, compute_type=self.compute_type,
                                  cpu_threads=cpu_threads)

    def transcribe(self, audio: Path, language: str, glossary: list[str]) -> Transcript:
        settings = {
            "device": self.device,
            "compute_type": self.compute_type,
            "beam_size": self.beam_size,
            "vad_filter": True,
            "condition_on_previous_text": False,  # limits runaway repetition/hallucination
            # faster-whisper re-applies `hotwords` to every 30 s window, whereas `initial_prompt`
            # is dropped after the first one when condition_on_previous_text is False.
            "hotwords": build_prompt(language, glossary),
        }
        started = time.monotonic()
        segments_iter, info = self.model.transcribe(
            str(audio),
            language=language,
            beam_size=self.beam_size,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 700},
            condition_on_previous_text=False,
            word_timestamps=True,
            hotwords=settings["hotwords"],
        )
        segments = []
        for s in segments_iter:  # decoding happens lazily while iterating
            words = [Word(w.start, w.end, w.word, w.probability) for w in (s.words or [])]
            segments.append(Segment(s.start, s.end, s.text.strip(), words))
            print(f"  [{s.start:7.1f}s] {s.text.strip()}", file=sys.stderr)
        elapsed = time.monotonic() - started
        return Transcript(
            language=info.language, duration=info.duration, segments=segments,
            engine=self.name, model=self.model_name, settings=settings, elapsed=round(elapsed, 2),
        )
