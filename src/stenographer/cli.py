"""`steno` command line.

    steno record                 record a session (Ctrl-C to stop), then transcribe it
    steno transcribe [PATH]      transcribe a session folder (default: latest) or import an audio file
    steno wer REF HYP            word error rate of a transcript against a hand-corrected reference
    steno guard RAW CLEAN        check a fair copy against the raw transcript
    steno watch INBOX            transcribe recordings arriving in a folder (e.g. from the phone)
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from . import guard as guard_mod
from . import pipeline
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
    p.add_argument("--root", type=Path, default=None,
                   help="folder holding session folders (default: $STENO_ROOT or ./sessions)")
    p.add_argument("--notes", type=Path, default=_env_path("STENO_NOTES"),
                   help="also write <session>.md here, e.g. a folder in your Obsidian vault "
                        "(default: $STENO_NOTES)")


def _env_path(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value).expanduser() if value else None


def _engine(args: argparse.Namespace):
    return get_engine(args.engine, model=args.model, device=args.device,
                      compute_type=args.compute_type)


def _transcribe(session: Path, args: argparse.Namespace, tag: str | None = None) -> None:
    transcript = pipeline.transcribe_session(session, _engine(args), args.language,
                                             sess.load_glossary(args.glossary), tag=tag)
    if args.notes and not tag:
        pipeline.write_note(session, transcript, args.notes)


def cmd_record(args: argparse.Namespace) -> None:
    from .record import record

    session = sess.new_session(args.root)
    seconds = record(session / sess.AUDIO_NAME, device=args.input, seconds=args.seconds)
    sess.write_meta(session, {"recorded_seconds": seconds})
    print(f"Saved {session / sess.AUDIO_NAME} ({seconds:.0f} s)", file=sys.stderr)
    if not args.no_transcribe:
        _transcribe(session, args)


def cmd_transcribe(args: argparse.Namespace) -> None:
    path = args.path or sess.latest_session(args.root)
    if path is None:
        raise SystemExit("No sessions yet. Run `steno record` or pass an audio file.")
    session = path if path.is_dir() else pipeline.import_audio(path, args.root)
    _transcribe(session, args, tag=args.tag)


def cmd_watch(args: argparse.Namespace) -> None:
    from .watch import Watcher

    watcher = Watcher(
        inbox=args.inbox, root=args.root or sess.default_root(),
        engine_factory=lambda: _engine(args), language=args.language,
        glossary_loader=lambda: sess.load_glossary(args.glossary),  # re-read: edits apply live
        notes_dir=args.notes, default_source=args.source, settle=args.settle,
    )
    try:
        watcher.run(interval=args.interval, once=args.once)
    except KeyboardInterrupt:
        pass


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
    p.add_argument("--tag", default=None,
                   help="write raw.<tag>.md/json instead of raw.md/json (for engine comparisons)")
    p.set_defaults(func=cmd_transcribe)

    p = sub.add_parser("watch", help="transcribe recordings that arrive in an inbox folder")
    p.add_argument("inbox", type=Path, help="folder the phone's recordings sync into")
    _add_engine_args(p)
    p.add_argument("--source", default="phone",
                   help="device name when the file name does not carry one (default: phone)")
    p.add_argument("--interval", type=float, default=3.0, help="seconds between scans")
    p.add_argument("--settle", type=float, default=5.0,
                   help="seconds a file must stop changing before it is imported")
    p.add_argument("--once", action="store_true", help="process what is there, then exit")
    p.set_defaults(func=cmd_watch)

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
