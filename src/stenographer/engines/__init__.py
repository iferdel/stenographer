"""Speech-to-text engines. Add new ones to `ENGINES` (e.g. parakeet, mlx-whisper, cloud APIs)."""

from __future__ import annotations

from .base import Engine, Segment, Transcript, Word

ENGINES = ("whisper",)


def get_engine(name: str, **kwargs) -> Engine:
    if name == "whisper":
        from .whisper import WhisperEngine

        return WhisperEngine(**{k: v for k, v in kwargs.items() if v is not None})
    raise SystemExit(f"Unknown engine '{name}'. Available: {', '.join(ENGINES)}")


__all__ = ["ENGINES", "Engine", "Segment", "Transcript", "Word", "get_engine"]
