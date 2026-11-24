"""Engine interface. Every speech-to-text backend (Whisper, Parakeet, MLX, cloud APIs)
implements `Engine.transcribe` and returns a `Transcript`, so the bake-off can swap them freely."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Protocol


@dataclass
class Word:
    start: float
    end: float
    text: str
    probability: float | None = None


@dataclass
class Segment:
    start: float
    end: float
    text: str
    words: list[Word] = field(default_factory=list)


@dataclass
class Transcript:
    language: str
    duration: float
    segments: list[Segment]
    engine: str
    model: str
    settings: dict = field(default_factory=dict)
    elapsed: float = 0.0  # wall-clock seconds spent transcribing

    @property
    def text(self) -> str:
        """One paragraph per segment."""
        return "\n\n".join(s.text.strip() for s in self.segments if s.text.strip())

    @property
    def real_time_factor(self) -> float:
        return self.elapsed / self.duration if self.duration else 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class Engine(Protocol):
    name: str

    def transcribe(self, audio: Path, language: str, glossary: list[str]) -> Transcript: ...
