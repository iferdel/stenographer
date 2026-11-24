import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from stenographer.engines import Segment, Transcript
from stenographer.watch import STATE_NAME, Watcher, is_candidate, parse_name

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not installed")


class FakeEngine:
    name = "fake"

    def __init__(self):
        self.calls = []

    def transcribe(self, audio, language, glossary):
        self.calls.append((audio, language, glossary))
        return Transcript(language, 2.0, [Segment(0, 2, "—Hola —dijo Polina.")], "fake", "m")


def _tone(path: Path, seconds: float = 2) -> None:
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi",
                    "-i", f"sine=frequency=440:duration={seconds}", str(path)], check=True)


def test_parse_name_patterns():
    assert parse_name(Path("2026-11-23_223220_iphone.m4a")) == (
        datetime(2026, 11, 23, 22, 32, 20), "iphone")
    assert parse_name(Path("Recording 20261123223220.webm")) == (
        datetime(2026, 11, 23, 22, 32, 20), None)
    assert parse_name(Path("Nota de voz.m4a")) == (None, None)


def test_candidates(tmp_path):
    for name in ["a.m4a", "b.WEBM", ".hidden.m4a", "c.m4a.tmp", ".syncthing.d.m4a.tmp", "x.md"]:
        (tmp_path / name).write_bytes(b"x")
    assert sorted(p.name for p in tmp_path.iterdir() if is_candidate(p)) == ["a.m4a", "b.WEBM"]


def test_inbox_inside_root_is_refused(tmp_path):
    with pytest.raises(SystemExit):
        Watcher(tmp_path / "s" / "inbox", tmp_path / "s", FakeEngine, "es", list, None)


def test_settle_waits_for_file_to_stop_changing(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    f = inbox / "rec.m4a"
    f.write_bytes(b"12345")
    w = Watcher(inbox, tmp_path / "sessions", FakeEngine, "es", list, None, settle=5)
    assert w.ready_files(now=0) == []  # first sighting
    assert w.ready_files(now=4) == []  # not settled yet
    assert w.ready_files(now=6) == [f]


@needs_ffmpeg
def test_watch_once_imports_transcribes_and_writes_vault_note(tmp_path):
    vault = tmp_path / "vault"
    (vault / ".obsidian").mkdir(parents=True)
    inbox = vault / "Dictado" / "inbox"
    inbox.mkdir(parents=True)
    notes = vault / "Dictado"
    rec = inbox / "2026-11-23_223220_iphone.m4a"
    _tone(rec)

    engine = FakeEngine()
    w = Watcher(inbox, tmp_path / "sessions", lambda: engine, "es", lambda: ["Polina"], notes,
                settle=0)
    w.run(interval=0, once=True)

    session = tmp_path / "sessions" / "2026-11-23_223220_iphone"
    assert (session / "audio.flac").exists()
    assert (session / "raw.md").read_text(encoding="utf-8") == "—Hola —dijo Polina.\n"
    meta = json.loads((session / "meta.json").read_text(encoding="utf-8"))
    assert meta["source"] == "iphone" and meta["recorded"] == "2026-11-23T22:32:20"
    assert engine.calls[0][2] == ["Polina"]

    note = (notes / "2026-11-23_223220_iphone.md").read_text(encoding="utf-8")
    assert note.startswith("---\n") and "![[2026-11-23_223220_iphone.m4a]]" in note
    assert note.rstrip().endswith("—Hola —dijo Polina.")

    assert rec.exists()  # original untouched, so Obsidian embeds keep working
    state = json.loads((inbox / STATE_NAME).read_text(encoding="utf-8"))
    assert list(state.values())[0]["session"] == str(session)

    w2 = Watcher(inbox, tmp_path / "sessions", lambda: engine, "es", list, notes, settle=0)
    w2.run(interval=0, once=True)
    assert len(engine.calls) == 1  # already imported: not processed again


@needs_ffmpeg
def test_broken_file_is_recorded_not_retried(tmp_path):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "broken.m4a").write_bytes(b"not audio")
    w = Watcher(inbox, tmp_path / "sessions", FakeEngine, "es", list, None, settle=0)
    w.run(interval=0, once=True)
    state = json.loads((inbox / STATE_NAME).read_text(encoding="utf-8"))
    assert "error" in state["broken.m4a|9"]
    assert not any((tmp_path / "sessions").iterdir())  # half-made session cleaned up
