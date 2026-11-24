"""`steno` command line.

    steno record                 record a session (Ctrl-C to stop), then transcribe it
    steno transcribe [PATH]      transcribe a session folder (default: latest) or import an audio file
    steno wer REF HYP            word error rate of a transcript against a hand-corrected reference
    steno guard RAW CLEAN        check a fair copy against the raw transcript
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from . import guard as guard_mod
from . import session as sess
from . import wer as wer_mod
from .engines import ENGINES, get_engine


def _add_engine_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--engine", default="whisper", choices=ENGINES)
    p.add_argument("--model", default=None, help="engine model name (whisper: large-v3-turbo)")
    p.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    p.add_argument("--compute-type", default=None, help="override, e.g. int8, float16")
    p.add_argument("--language", default="es")
    p.add_argument("--glossary", type=Path, default=Path("glossary.txt"),
                   help="names/unusual words, one per line (default: ./glossary.txt if present)")
    p.add_argument("--tag", default=None,
                   help="write raw.<tag>.md/json instead of raw.md/json (for engine comparisons)")


def _import_audio(audio: Path) -> Path:
    session = sess.new_session()
    subprocess.run(
        [shutil.which("ffmpeg") or "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
         "-i", str(audio), "-ac", "1", "-ar", "16000", str(session / sess.AUDIO_NAME)],
        check=True,
    )
    sess.write_meta(session, {"imported_from": str(audio.resolve())})
    return session


def _transcribe_session(session: Path, args: argparse.Namespace) -> None:
    audio = session / sess.AUDIO_NAME
    if not audio.exists():
        raise SystemExit(f"No {sess.AUDIO_NAME} in {session}")
    glossary = sess.load_glossary(args.glossary)
    engine = get_engine(args.engine, model=args.model, device=args.device,
                        compute_type=args.compute_type)
    print(f"Transcribing {audio} with {engine.name} …", file=sys.stderr)
    transcript = engine.transcribe(audio, args.language, glossary)

    stem = f"raw.{args.tag}" if args.tag else "raw"
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


def _vram_mb() -> int | None:
    """Best effort: VRAM held by this process after transcription, read via nvidia-smi."""
    if not shutil.which("nvidia-smi"):
        return None
    import os

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


def cmd_record(args: argparse.Namespace) -> None:
    from .record import record

    session = sess.new_session()
    seconds = record(session / sess.AUDIO_NAME, device=args.input, seconds=args.seconds)
    sess.write_meta(session, {"recorded_seconds": seconds})
    print(f"Saved {session / sess.AUDIO_NAME} ({seconds:.0f} s)", file=sys.stderr)
    if not args.no_transcribe:
        _transcribe_session(session, args)


def cmd_transcribe(args: argparse.Namespace) -> None:
    path = args.path or sess.latest_session()
    if path is None:
        raise SystemExit("No sessions yet. Run `steno record` or pass an audio file.")
    session = path if path.is_dir() else _import_audio(path)
    _transcribe_session(session, args)


def cmd_wer(args: argparse.Namespace) -> None:
    result = wer_mod.compute_wer(args.reference.read_text(encoding="utf-8"),
                                 args.hypothesis.read_text(encoding="utf-8"))
    print(wer_mod.format_report(result, top=args.top))


def cmd_guard(args: argparse.Namespace) -> None:
    result = guard_mod.check(args.raw.read_text(encoding="utf-8"),
                             args.clean.read_text(encoding="utf-8"), max_rate=args.max_rate)
    print(guard_mod.format_report(result))
    sys.exit(0 if result.passed else 1)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="steno", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("record", help="record a dictation session, then transcribe it")
    p.add_argument("--input", default=None,
                   help="capture device (Linux: PipeWire node name/serial; macOS: avfoundation index)")
    p.add_argument("--seconds", type=float, default=None, help="stop after N seconds")
    p.add_argument("--no-transcribe", action="store_true")
    _add_engine_args(p)
    p.set_defaults(func=cmd_record)

    p = sub.add_parser("transcribe", help="transcribe a session folder or an audio file")
    p.add_argument("path", nargs="?", type=Path, help="session folder or audio file (default: latest session)")
    _add_engine_args(p)
    p.set_defaults(func=cmd_transcribe)

    p = sub.add_parser("wer", help="word error rate against a hand-corrected reference")
    p.add_argument("reference", type=Path)
    p.add_argument("hypothesis", type=Path)
    p.add_argument("--top", type=int, default=30)
    p.set_defaults(func=cmd_wer)

    p = sub.add_parser("guard", help="check a fair copy against the raw transcript")
    p.add_argument("raw", type=Path)
    p.add_argument("clean", type=Path)
    p.add_argument("--max-rate", type=float, default=0.0,
                   help="allowed share of changed words (default 0: any word change rejects)")
    p.set_defaults(func=cmd_guard)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
