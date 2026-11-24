"""Session folders: one per dictation sitting, holding audio, raw transcript and metadata.

Layout (this is the contract a future Rust port must keep reading and writing):

    sessions/YYYY-MM-DD_HHMMSS/
        audio.flac   the recording, source of truth
        raw.json     engine output: segments with word timestamps
        raw.md       plain text, one paragraph per pause-delimited segment
        meta.json    who/what/how produced the files above
        <name>.md    optional Obsidian note (front matter + audio embed + text); derived,
                     never read back by the tool
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path

from . import __version__

AUDIO_NAME = "audio.flac"


def default_root() -> Path:
    """Where session folders live: $STENO_ROOT if set (e.g. a folder inside an Obsidian vault),
    otherwise ./sessions."""
    return Path(os.environ.get("STENO_ROOT") or "sessions").expanduser()



def new_session(root: Path | None = None, source: str | None = None,
                when: datetime | None = None) -> Path:
    """Create sessions/YYYY-MM-DD_HHMMSS[_source]. `when` is the recording time (default: now);
    `source` names the device (e.g. "iphone") so sessions from different devices never collide;
    a -2, -3… suffix covers the rest."""
    root = root if root is not None else default_root()
    name = (when or datetime.now()).strftime("%Y-%m-%d_%H%M%S")
    if source:
        name += "_" + re.sub(r"[^A-Za-z0-9-]+", "-", source).strip("-").lower()
    path, n = root / name, 1
    while True:
        try:
            path.mkdir(parents=True, exist_ok=False)
            break
        except FileExistsError:
            n += 1
            path = root / f"{name}-{n}"
    meta = {"created": datetime.now().isoformat(timespec="seconds")}
    if when:
        meta["recorded"] = when.isoformat(timespec="seconds")
    if source:
        meta["source"] = source
    write_meta(path, meta)
    return path


def read_meta(session: Path) -> dict:
    meta_path = session / "meta.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return {}


def write_meta(session: Path, updates: dict) -> dict:
    meta = read_meta(session)
    meta.update(updates)
    meta["tool_version"] = __version__
    (session / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return meta


def load_glossary(path: Path | None) -> list[str]:
    """One term per line; blank lines and lines starting with # are ignored."""
    if path is None or not path.exists():
        return []
    terms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(line)
    return terms


def glossary_hash(terms: list[str]) -> str | None:
    if not terms:
        return None
    return hashlib.sha256("\n".join(terms).encode("utf-8")).hexdigest()[:12]


def latest_session(root: Path | None = None) -> Path | None:
    root = root if root is not None else default_root()
    if not root.exists():
        return None
    sessions = sorted(p for p in root.iterdir() if p.is_dir())
    return sessions[-1] if sessions else None
