# Stenographer

Dictate a book by voice, the way Dostoevsky dictated *The Gambler* to Anna Snitkina:
speak a session, get a faithful transcript, revise the fair copy. Python prototype (v0).
Background research: `reports/Voice dictation stack for books.md`.

## Setup

```sh
uv sync            # Python 3.12, faster-whisper, CUDA libraries as pip wheels (Linux)
```

The first transcription downloads Whisper large-v3-turbo (~1.6 GB) from Hugging Face.

## Use

```sh
uv run steno record                    # speak; Ctrl-C to stop; then it transcribes
uv run steno record --no-transcribe    # just record
uv run steno transcribe                # (re)transcribe the latest session
uv run steno transcribe path/to.mp3    # import an audio file as a new session
uv run steno wer reference.md sessions/<id>/raw.md   # bake-off: word error rate
uv run steno guard sessions/<id>/raw.md clean.md     # check a fair copy against the raw text
uv run steno watch ~/Vault/Dictado/inbox --notes ~/Vault/Dictado   # transcribe phone recordings
```

Useful flags: `--device cpu|cuda`, `--model <whisper model>`, `--tag <name>` (writes
`raw.<name>.md` so several engines/models can sit side by side in one session),
`--glossary file` (default `./glossary.txt`: character names and unusual words, one per line),
`--root dir` or `$STENO_ROOT` (where session folders go, default `./sessions`),
`--notes dir` or `$STENO_NOTES` (also write an Obsidian note per session), `--input <device>`
for `record`.

Each session is a folder `sessions/YYYY-MM-DD_HHMMSS/`:

| File | Content |
|---|---|
| `audio.flac` | 16 kHz mono recording, the source of truth (kept out of git) |
| `raw.json` | segments with word timestamps and probabilities |
| `raw.md` | plain transcript, one paragraph per pause-delimited segment |
| `meta.json` | engine, model, settings, prompt, glossary hash, timings, VRAM, source device |

Session names are `YYYY-MM-DD_HHMMSS[_device]`, using the recording time when known.

## Dictating on the phone (Obsidian)

The phone only records; the laptop transcribes and the text syncs back as a note.

```
iPhone: record → <vault>/Dictado/inbox/2026-11-23_224500_iphone.m4a
        ─ Obsidian Sync ─▶ laptop: steno watch <vault>/Dictado/inbox --notes <vault>/Dictado
        ◀─ Obsidian Sync ─ <vault>/Dictado/2026-11-23_224500_iphone.md (text + audio embed)
```

- **Session folders stay outside the vault** (default `./sessions`). 16 kHz FLAC is about 100 MB
  per hour and would fill sync storage; only the small note goes into the vault. The note
  embeds the phone's original recording, which is already in the vault.
- **Originals are never moved or renamed**, so `![[Recording ….m4a]]` embeds made by
  Obsidian's audio recorder keep working; the inbox can be the vault's attachment folder.
  Processed files are listed in `<inbox>/.steno-imported.json` (delete an entry to redo one;
  failures are recorded there too, with the error, and not retried).
- A file is imported once it has stopped changing for `--settle` seconds (default 5).
  Any audio ffmpeg reads works (m4a, webm, caf, mp3, ogg, wav, flac…).
- File names like `2026-11-23_224500_iphone.m4a` or `Recording 20261123224500.webm` give the
  recording time and device; otherwise the file's mtime and `--source` (default `phone`).
- Obsidian Sync only runs while the Obsidian app is open, on the laptop and on the phone (iOS
  syncs in the foreground), so keep Obsidian open on the laptop while `steno watch` runs.
- Phone-side recording settings are untested on a device (see below).

**iOS Shortcut (one tap, e.g. on the Action Button)** (untested):
1. Record Audio (Start immediately, Finish on tap).
2. Format Date: Current Date, custom format `yyyy-MM-dd_HHmmss`.
3. Set Name of the recording to `<formatted date>_iphone`.
4. Save File to On My iPhone › Obsidian › <vault> › Dictado › inbox, "Ask Where to Save" off.
5. Open URL `obsidian://open?vault=<vault>` so Obsidian syncs the file right away.

## The diff guard

`steno guard` aligns the fair copy with the raw transcript word by word. Punctuation, case,
paragraphing and dialogue layout (rayas, ¿ ¡) are free. Dropping pure hesitations (`eh`,
`mmm`) and stutter repeats (`el el`) is allowed. Every other word change (substitution,
addition, deletion, accent change) is listed, and the copy is rejected if those exceed
`--max-rate` (default 0). Even a correct fix of a mis-heard word is listed, so you approve it.

## Measured on this machine (GTX 1650 4 GB, Debian 12)

A 3:44 LibriVox chapter in Spanish (Valle-Inclán) took 26 s: real-time factor 0.11, about
960 MB VRAM, `int8_float16`. Without a punctuated prompt, turbo returned unpunctuated
lowercase text, so a Spanish style prompt is always sent (`engines/whisper.py`). Errors were
in literary vocabulary: *colleras → colinas*, *quedéme → quedé me*, *ejercíalo → ejercía lo*.

## Next steps

1. Bake-off: record 30 min of your own prose (with dialogue and the book's names), hand-correct a
   reference, compare `--model large-v3-turbo` vs others with `--tag`, then add Parakeet v3 and a
   cloud engine behind `engines/base.py`.
2. Calibrate the guard on real sessions (filler list, `--max-rate`).
3. Fair-copy stage: LLM cleanup per segment, scored by the guard from the first run.
4. On the M1 Mac: add an MLX engine (`mlx-whisper`); CPU `int8` works meanwhile.

## Rust checkpoint

Stay in Python until **all** of these hold:

1. One full chapter has gone through record → transcribe → fair copy → revision.
2. The speech engine is chosen from the bake-off and unchanged for two weeks of real use.
3. The session-folder format and guard rules have not changed for two weeks.

Then port to Rust only if **at least one** of these is true:

- You want a persistent desktop app: global hotkey, tray, live preview, revision UI (Tauri).
- Python is causing concrete pain: startup time, CUDA or dependency breakage, Mac packaging.
- The chosen engine has a solid Rust path (`whisper-rs`, or ONNX via `ort` for Parakeet). If the
  winner is MLX-only or Python-only, keep the engine as a Python worker and port the rest.

The session folder (FLAC, JSON, Markdown) is the contract between the two implementations, so a
port can be gradual and old sessions stay readable. Keep the guard's unit tests
(`tests/test_guard.py`) as the spec a Rust guard must pass.
