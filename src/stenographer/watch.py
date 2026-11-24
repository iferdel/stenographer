"""`steno watch`: transcribe recordings that arrive in an inbox folder (e.g. from the phone via
Obsidian Sync, iCloud or Syncthing).

Originals are never moved or renamed: Obsidian only repairs embeds when a file is moved from
inside Obsidian, so moving them would break `![[Recording ….m4a]]` links in notes. Processed
files are remembered in <inbox>/.steno-imported.json instead (delete an entry to redo it).
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

from .engines import Engine
from . import pipeline

AUDIO_EXTS = {".m4a", ".aac", ".caf", ".webm", ".ogg", ".opus", ".mp3", ".wav", ".flac", ".mp4"}
STATE_NAME = ".steno-imported.json"

# 2026-11-23_223220_iphone.m4a (iOS Shortcut), 2026-11-23 22.32.20.m4a,
# Recording 20261123223220.webm (Obsidian audio recorder).
_STAMP = re.compile(
    r"(?P<y>\d{4})-?(?P<mo>\d{2})-?(?P<d>\d{2})[ _T-]?(?P<h>\d{2})[.:-]?(?P<mi>\d{2})[.:-]?(?P<s>\d{2})"
    r"(?:_(?P<src>[A-Za-z][A-Za-z0-9-]*))?"
)


def parse_name(path: Path) -> tuple[datetime | None, str | None]:
    """Recording time and device from the file name, when the name carries them."""
    m = _STAMP.search(path.stem)
    if not m:
        return None, None
    try:
        when = datetime(*(int(m[k]) for k in ("y", "mo", "d", "h", "mi", "s")))
    except ValueError:
        return None, None
    return when, m["src"]


def vault_root(path: Path) -> Path | None:
    """The Obsidian vault containing `path` (the nearest folder with a .obsidian directory)."""
    path = path.resolve()
    for folder in (path, *path.parents):
        if (folder / ".obsidian").is_dir():
            return folder
    return None


def is_candidate(path: Path) -> bool:
    name = path.name
    if not path.is_file() or name.startswith((".", "~")):
        return False
    if name.endswith((".tmp", ".part", ".crdownload")) or ".syncthing." in name:
        return False
    return path.suffix.lower() in AUDIO_EXTS


class Watcher:
    def __init__(self, inbox: Path, root: Path, engine_factory: Callable[[], Engine],
                 language: str, glossary_loader: Callable[[], list[str]],
                 notes_dir: Path | None, default_source: str = "phone", settle: float = 5.0):
        self.inbox, self.root = inbox.resolve(), root.resolve()
        if self.inbox == self.root or self.root in self.inbox.parents or self.inbox in self.root.parents:
            raise SystemExit("The inbox and the session root must not contain each other.")
        self.engine_factory, self.engine = engine_factory, None
        self.language, self.glossary_loader = language, glossary_loader
        self.notes_dir, self.default_source, self.settle = notes_dir, default_source, settle
        self.state_path = self.inbox / STATE_NAME
        self.state: dict = (json.loads(self.state_path.read_text(encoding="utf-8"))
                            if self.state_path.exists() else {})
        self._seen: dict[Path, tuple[int, float, float]] = {}  # path -> (size, mtime, since)

    @staticmethod
    def key(path: Path) -> str:
        # Name + size, not mtime: sync tools may rewrite mtimes when they re-download a file.
        return f"{path.name}|{path.stat().st_size}"

    def _save_state(self) -> None:
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        tmp.replace(self.state_path)

    def ready_files(self, now: float | None = None) -> list[Path]:
        """New audio files whose size and mtime have not changed for `settle` seconds
        (a file still being written or synced keeps growing)."""
        now = time.monotonic() if now is None else now
        ready = []
        for path in sorted(self.inbox.iterdir()):
            if not is_candidate(path) or self.key(path) in self.state:
                continue
            st = path.stat()
            prev = self._seen.get(path)
            if prev is None or prev[:2] != (st.st_size, st.st_mtime):
                self._seen[path] = (st.st_size, st.st_mtime, now)
                if self.settle > 0:
                    continue
            if st.st_size > 0 and now - self._seen[path][2] >= self.settle:
                ready.append(path)
        return ready

    def process(self, path: Path) -> None:
        key = self.key(path)
        when, source = parse_name(path)
        when = when or datetime.fromtimestamp(path.stat().st_mtime)
        source = source or self.default_source
        print(f"\n● {path.name}", file=sys.stderr)
        try:
            session = pipeline.import_audio(path, self.root, source=source, when=when)
            if self.engine is None:
                self.engine = self.engine_factory()
            transcript = pipeline.transcribe_session(session, self.engine, self.language,
                                                     self.glossary_loader())
            if self.notes_dir:
                # Embed the original only if Obsidian can resolve it: same vault as the note.
                vault = vault_root(self.notes_dir)
                embed = path.name if vault and vault in path.resolve().parents else None
                pipeline.write_note(session, transcript, self.notes_dir, embed=embed)
        except Exception as exc:  # keep watching; record the failure so it is not retried forever
            print(f"  ✗ failed: {exc}", file=sys.stderr)
            self.state[key] = {"error": str(exc), "at": datetime.now().isoformat(timespec="seconds")}
        else:
            self.state[key] = {"session": str(session),
                               "at": datetime.now().isoformat(timespec="seconds")}
        self._seen.pop(path, None)
        self._save_state()

    def run(self, interval: float = 3.0, once: bool = False) -> None:
        print(f"Watching {self.inbox} → {self.root}"
              + (f" (notes → {self.notes_dir})" if self.notes_dir else ""), file=sys.stderr)
        while True:
            for path in self.ready_files():
                self.process(path)
            if once and not any(is_candidate(p) and self.key(p) not in self.state
                                for p in self.inbox.iterdir()):
                return
            time.sleep(interval)
