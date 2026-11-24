"""Microphone capture to FLAC.

Linux: pw-record (PipeWire). macOS: ffmpeg with AVFoundation.
Records 16 kHz mono, which is what the speech models consume. No noise suppression:
the research found it tends to hurt Whisper-class recognition.
"""

from __future__ import annotations

import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

RATE = 16000


def _require(tool: str) -> str:
    path = shutil.which(tool)
    if path is None:
        raise SystemExit(f"'{tool}' not found on PATH; it is needed for recording.")
    return path


def _capture_command(wav_path: Path, device: str | None) -> list[str]:
    if sys.platform == "darwin":
        # ":0" = default audio input, no video. List devices with:
        #   ffmpeg -f avfoundation -list_devices true -i ""
        source = f":{device}" if device else ":0"
        return [
            _require("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
            "-f", "avfoundation", "-i", source,
            "-ac", "1", "-ar", str(RATE), "-sample_fmt", "s16", str(wav_path),
        ]
    cmd = [
        _require("pw-record"), "--rate", str(RATE), "--channels", "1",
        "--format", "s16", "--media-role", "Communication",
    ]
    if device:
        cmd += ["--target", device]
    return cmd + [str(wav_path)]


def record(flac_path: Path, device: str | None = None, seconds: float | None = None) -> float:
    """Record until Ctrl-C (or for `seconds`), then encode to FLAC. Returns duration in seconds."""
    wav_path = flac_path.with_suffix(".wav")
    proc = subprocess.Popen(_capture_command(wav_path, device), stdin=subprocess.DEVNULL)
    started = time.monotonic()
    print("Grabando… pulsa Ctrl-C para terminar." if seconds is None else f"Grabando {seconds:g} s…",
          file=sys.stderr)
    try:
        if seconds is None:
            proc.wait()
        else:
            try:
                proc.wait(timeout=seconds)
            except subprocess.TimeoutExpired:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    elapsed = time.monotonic() - started

    if not wav_path.exists() or wav_path.stat().st_size <= 44:
        raise SystemExit("No audio was captured. Check the microphone / recorder output above.")

    subprocess.run(
        [_require("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y",
         "-i", str(wav_path), "-ac", "1", "-ar", str(RATE), str(flac_path)],
        check=True,
    )
    wav_path.unlink()
    return round(elapsed, 2)
