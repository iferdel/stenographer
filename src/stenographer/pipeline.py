"""The work shared by every command: import audio into a session, transcribe a session, and
write the optional Obsidian note."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from . import session as sess
from .engines import Engine, Transcript


def import_audio(audio: Path, root: Path | None = None, source: str | None = None,
                 when: datetime | None = None) -> Path:
    """Convert any audio ffmpeg can read (m4a, webm, mp3, …) to 16 kHz mono FLAC in a new session."""
    session = sess.new_session(root, source=source, when=when)
    try:
        subprocess.run(
            [shutil.which("ffmpeg") or "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-i", str(audio), "-ac", "1", "-ar", "16000", str(session / sess.AUDIO_NAME)],
            check=True,
        )
    except subprocess.CalledProcessError:
        shutil.rmtree(session, ignore_errors=True)
        raise
    sess.write_meta(session, {"imported_from": str(audio.resolve())})
    return session


def transcribe_session(session: Path, engine: Engine, language: str, glossary: list[str],
                       tag: str | None = None) -> Transcript:
    audio = session / sess.AUDIO_NAME
    if not audio.exists():
        raise SystemExit(f"No {sess.AUDIO_NAME} in {session}")
    print(f"Transcribing {audio} with {engine.name} …", file=sys.stderr)
    transcript = engine.transcribe(audio, language, glossary)

    stem = f"raw.{tag}" if tag else "raw"
    (session / f"{stem}.json").write_text(
        json.dumps(transcript.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (session / f"{stem}.md").write_text(transcript.text + "\n", encoding="utf-8")

    vram = _vram_mb()
    sess.write_meta(session, {stem: {
        "engine": transcript.engine,
        "model": transcript.model,
        "settings": transcript.settings,
        "language": transcript.language,
        "audio_seconds": round(transcript.duration, 2),
        "transcribe_seconds": transcript.elapsed,
        "real_time_factor": round(transcript.real_time_factor, 3),
        "glossary_terms": len(glossary),
        "glossary_hash": sess.glossary_hash(glossary),
        "vram_mb": vram,
    }})
    words = sum(len(s.text.split()) for s in transcript.segments)
    print(
        f"\n{words} words, {transcript.duration:.1f} s of audio in {transcript.elapsed:.1f} s "
        f"(RTF {transcript.real_time_factor:.2f}, {transcript.settings.get('device')}"
        f" {transcript.settings.get('compute_type')}"
        + (f", VRAM {vram} MB" if vram else "") + ")",
        file=sys.stderr,
    )
    print(f"→ {session / (stem + '.md')}", file=sys.stderr)
    return transcript


def write_note(session: Path, transcript: Transcript, notes_dir: Path,
               embed: str | None = None) -> Path:
    """Write <session-id>.md into a notes folder (e.g. inside an Obsidian vault).

    Only this small note goes into the vault; the session folder with its FLAC stays outside,
    so audio does not fill sync storage. `embed` is the file name of an audio file that is
    already in the vault (the phone's original recording), embedded so it plays on any device.
    raw.md stays plain text; the note is derived output and never read back.
    """
    meta = sess.read_meta(session)
    words = sum(len(s.text.split()) for s in transcript.segments)
    minutes, seconds = divmod(round(transcript.duration), 60)
    front = {
        "date": meta.get("recorded") or meta.get("created"),
        "source": meta.get("source", "laptop"),
        "duration": f"{minutes}:{seconds:02d}",
        "words": words,
        "model": f"{transcript.engine} {transcript.model}",
        "session": str(session.resolve()),
    }
    lines = ["---"] + [f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in front.items()]
    lines += ["tags: [dictado]", "---", ""]
    if embed:
        lines += [f"![[{embed}]]", ""]
    lines.append(transcript.text)
    notes_dir.mkdir(parents=True, exist_ok=True)
    note = notes_dir / f"{session.name}.md"
    note.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"→ {note}", file=sys.stderr)
    return note


def _vram_mb() -> int | None:
    """Best effort: VRAM held by this process after transcription, read via nvidia-smi."""
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-compute-apps=pid,used_memory", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    for line in out.splitlines():
        pid, _, mem = line.partition(",")
        if pid.strip() == str(os.getpid()):
            return int(mem.strip())
    return None
