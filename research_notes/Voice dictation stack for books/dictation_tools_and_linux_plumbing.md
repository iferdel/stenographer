# Dictation tools and Linux audio/input plumbing (state as of 23 Nov 2026)

Method notes for the report writer:
- GitHub stars / last-push / latest-release figures were read directly from the GitHub API on 2026-11-23 (cited as the repo URL).
- Several facts about the user's own machine were checked locally on 2026-11-23 and are marked **[local check]** (no URL): glibc 2.36, session = GNOME on Wayland, `pw-record` and `arecord` present, `nvidia-smi` present, none of xdotool / ydotool / wtype / dotool installed; Debian 12 apt candidates are ydotool 0.1.8-3, wtype 0.4-3, xdotool 3.20160805; dotool is not packaged.
- Many web sources in this space are vendor blogs comparing themselves with competitors (OpenWhispr, Voibe, Voicy, Laxis, Spokenly). They are flagged where used.
- thecreativepenn.com returned HTTP 503 on both attempts, so Joanna Penn's material is only covered through search snippets.

---

## 1. Which dictation apps work on Linux in 2026, and how good are they?

### Takeaway
There is now a crowded, very actively maintained field of open-source local dictation apps on Linux (Handy, voxtype, hyprwhspr, OpenWhispr, Vocalinux, Speech Note, whisrs, Epicenter Whispering), almost all "hold/toggle a hotkey, record, transcribe on release, paste" tools built on Whisper (whisper.cpp / faster-whisper) and/or NVIDIA Parakeet V3; true streaming is rare and experimental. Among commercial tools, Superwhisper shipped a Linux app in November 2026 (Wayland; Debian listed), while Wispr Flow, Aqua Voice, Willow, MacWhisper and Dragon have no Linux app, and Talon has announced it is dropping Linux.

### Cited Findings

#### Open-source apps: repository status (GitHub API, 2026-11-23)

| Tool | Stars | Last push | Latest release | License | Language |
|---|---|---|---|---|---|
| [Handy](https://github.com/cjpais/Handy) | 39,905 | 2026-11-21 | v0.10.1 (2026-11-14) | MIT | Rust (Tauri) |
| [OpenWhispr](https://github.com/OpenWhispr/openwhispr) | 12,120 | 2026-11-24 | v1.12.0 (2026-11-17) | MIT | JavaScript |
| [Buzz](https://github.com/chidiwilliams/buzz) | 23,025 | 2026-11-20 | v1.4.5 (2026-08-23) | MIT | Python |
| [Vibe](https://github.com/thewh1teagle/vibe) | 8,215 | 2026-11-21 | v3.3.8 (2026-11-21) | MIT | TypeScript (Tauri) |
| [Epicenter (Whispering)](https://github.com/EpicenterHQ/epicenter) | 4,840 | 2026-11-24 | v7.x | GitHub reports no standard SPDX licence (NOASSERTION) | TypeScript |
| [nerd-dictation](https://github.com/ideasman42/nerd-dictation) | 1,948 | 2025-10-10 | none | GPL-3.0 | Python |
| [voxtype](https://github.com/peteonrails/voxtype) | 1,817 | 2026-11-23 | v1.3.1 (2026-11-22) | MIT | Rust |
| [Speech Note / dsnote](https://github.com/mkiol/dsnote) | 1,720 | 2026-11-22 | v4.9.0 (2026-06-28) | MPL-2.0 | C++ (Qt) |
| [hyprwhspr](https://github.com/goodroot/hyprwhspr) | 1,288 | 2026-11-23 | v1.58.0 (2026-11-23) | MIT | Python |
| [whisper-writer](https://github.com/savbell/whisper-writer) | 1,107 | 2024-08-24 | v1.0.1 (2024-01-29) | GPL-3.0 | Python |
| [Vocalinux](https://github.com/VocaHQ/vocalinux) | 1,039 | 2026-11-23 | v0.18.6 (2026-11-08) | AGPL-3.0 | Python |
| [whisrs](https://github.com/y0sif/whisrs) | 158 | 2026-11-22 | 0.1.x | MIT | Rust |
| [WhisperTux](https://github.com/cjams/whispertux) | 77 | 2026-04-22 | no releases | MIT | Python |

- The old standalone `braden-w/whispering` repository is archived (last push 2025-09-25); the project lives on inside the Epicenter monorepo — [braden-w/whispering](https://github.com/braden-w/whispering), [EpicenterHQ/epicenter](https://github.com/EpicenterHQ/epicenter)
- whisper-writer has had no push since August 2024 and no release since January 2024: effectively unmaintained — [savbell/whisper-writer](https://github.com/savbell/whisper-writer)
- nerd-dictation has had no push since October 2025; it is a VOSK-based script — [ideasman42/nerd-dictation](https://github.com/ideasman42/nerd-dictation); described as "a very lightweight wrapper around the Vosk model" and as requiring xdotool (X11) with limited Wayland support — [OpenWhispr blog (vendor)](https://openwhispr.com/blog/best-dictation-tools-linux-2026)

#### Handy (the reference design for a Rust/Tauri build)
- Engines: "Whisper models (Small/Medium/Turbo/Large) with GPU acceleration when available" and "Parakeet V3 – CPU-optimized model with excellent performance and automatic language detection"; custom Whisper GGML models dropped in the `models` directory are auto-discovered — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- Interaction: hold shortcut to record and release to stop, or tap to toggle; silence is filtered with Silero VAD; transcription happens after release (no streaming described) — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- Linux text input: uses `xdotool` (X11), `wtype` (Wayland, preferred) or `dotool` (both, needs `input` group); "Without these tools, Handy falls back to enigo which may have limited compatibility, especially on Wayland"; README calls Wayland support "limited" — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- On Ubuntu 26.04 (GNOME Wayland default) `wtype` does not work and the README points to `ydotool`; global shortcuts on Wayland are to be configured in the desktop environment, calling `handy --toggle-transcription` (or `pkill -USR2 -n handy`) — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- Has an LLM post-processing toggle (`handy --toggle-post-process`) and a transcription hook: "Handy writes the text to its stdin, after any LLM post-processing, and pastes its stdout" — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- Ships a `.deb` (install with APT, not `dpkg -i`) and an AppImage; the recording overlay is disabled by default on Linux because it can steal focus and break pasting — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- Spanish: Parakeet V2 is English-only; V3 is the multilingual one. Anecdotal HN comment on a Handy thread: "In Spanish works very well" — [HN thread on Handy](https://hn.svelte.dev/item/46628397)
- One HN commenter reported Handy on Linux as "quite slow" despite an available GPU — [HN item](https://news.ycombinator.com/item?id=50077458)

#### voxtype
- Rust, Wayland-first but also X11; "Nine transcription engines" including Whisper (default), Parakeet, Moonshine, Cohere Transcribe; Whisper covers 99 languages — [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md)
- Push-to-talk or toggle ("Hold to record, or press once to start/stop"); hotkey via compositor keybinding, with a built-in evdev fallback (user must be in `input` group) — [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md)
- Output chain: wtype preferred, "Falls back through dotool → ydotool → clipboard if any layer is unavailable" — [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md)
- "an optional post-processing pipe through any LLM or shell script" (stdin → stdout; falls back to raw text on failure) — [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md)
- GPU: prebuilt Vulkan binary plus separate CUDA 12 / CUDA 13 binaries — [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md)
- **Prebuilt packages require "glibc 2.38+ (Ubuntu 24.04+, Fedora 39+, Arch, Debian Trixie+)"** — [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md). The user's Debian 12 has glibc 2.36 **[local check]**, so prebuilt voxtype binaries will not run there; a source build would be needed.

#### Speech Note (dsnote)
- STT engines: Coqui STT, Vosk, whisper.cpp + Parakeet, Faster Whisper, april-asr, Qwen3-ASR; Spanish is marked supported for Whisper, Vosk and DeepSpeech — [dsnote README](https://raw.githubusercontent.com/mkiol/dsnote/main/README.md)
- Can "insert the decoded text into any window" via global shortcut or CLI action; "Under X11, this feature should work right out of the box"; "Under Wayland, the external `ydotool` daemon must be installed and running" — [dsnote README](https://raw.githubusercontent.com/mkiol/dsnote/main/README.md)
- Global shortcuts use the XDG GlobalShortcuts portal: "Currently, `GlobalShortcuts` is supported only in the latest KDE Plasma and GNOME desktops" — [dsnote README](https://raw.githubusercontent.com/mkiol/dsnote/main/README.md)
- Distributed as Flatpak (bundles its own runtime, so not affected by host glibc); the NVIDIA/CUDA add-on is ~4.3 GiB download, ~9 GiB unpacked, ~15 GiB needed during install; also includes offline translation (Bergamot), TTS and punctuation restoration — [dsnote README](https://raw.githubusercontent.com/mkiol/dsnote/main/README.md)
- It also has its own notepad buffer (speech goes into the app's text area) in addition to active-window insertion — [It's FOSS, 19 Nov 2026](https://itsfoss.com/voice-typing-tools-linux/)
- Conflicting quality assessment: OpenWhispr's blog says Speech Note's recognition accuracy is far below modern Whisper tools and "not recommended for new users" — [OpenWhispr blog (competitor)](https://openwhispr.com/blog/best-dictation-tools-linux-2026); this is contradicted by the README, which shows it runs the same whisper.cpp / Faster Whisper / Parakeet engines — [dsnote README](https://raw.githubusercontent.com/mkiol/dsnote/main/README.md)

#### hyprwhspr
- Despite the name, not Hyprland/Arch-only: "Supports NixOS, Arch, Debian, Ubuntu, Fedora, openSUSE and more"; "Wayland or X11 session (GNOME, KDE Plasma, Sway, Hyprland, Niri, etc.)" — [hyprwhspr README](https://raw.githubusercontent.com/goodroot/hyprwhspr/main/README.md)
- Backends: "Cohere / Parakeet / Whisper / Qwen3-ASR / ElevenLabs / REST API", optional cloud (Gemini, ElevenLabs, Deepgram) — [hyprwhspr README](https://raw.githubusercontent.com/goodroot/hyprwhspr/main/README.md)
- One of the few with streaming: "Live streaming - Self-host NeMo or Phonon: watch words form, or type as you speak (experimental)"; also a long-form mode ("Pause, think, resume, pause: submit") — [hyprwhspr README](https://raw.githubusercontent.com/goodroot/hyprwhspr/main/README.md)
- Text output via `wl-clipboard` + `wtype` on Wayland, `xdotool`/`xclip` on X11; post-transcription hook; detects CUDA / Vulkan / CPU and can unload the model from VRAM — [hyprwhspr README](https://raw.githubusercontent.com/goodroot/hyprwhspr/main/README.md), [It's FOSS](https://itsfoss.com/voice-typing-tools-linux/)

#### OpenWhispr
- Electron app, MIT; local engines Whisper (whisper.cpp) and Parakeet / Cohere Transcribe (sherpa-onnx), "GPU-accelerated local Whisper on Metal, CUDA, and Vulkan"; packages `.AppImage / .deb / .rpm / .tar.gz` — [OpenWhispr README](https://raw.githubusercontent.com/OpenWhispr/openwhispr/main/README.md)
- Strongest LLM integration of the open-source set: agent/voice-assistant hotkey that can talk to "GPT-5, Claude, Gemini, Groq, Tinfoil, OpenRouter, or local models" and edit highlighted text; custom dictionary; "100+ languages" — [OpenWhispr README](https://raw.githubusercontent.com/OpenWhispr/openwhispr/main/README.md)
- Freemium: local use and BYO API keys are free; hosted cloud free tier is "2,000 hosted words/week"; paid tiers for unlimited cloud — [OpenWhispr README](https://raw.githubusercontent.com/OpenWhispr/openwhispr/main/README.md)

#### Vocalinux, whisrs, Epicenter Whispering, WhisperTux, others
- Vocalinux: X11 and Wayland; engines whisper.cpp (default), Whisper, Faster Whisper, VOSK, Parakeet; voice commands such as "delete that" — [It's FOSS](https://itsfoss.com/voice-typing-tools-linux/). v0.18.0 added a RemoteDesktop-portal (libei) text-injection backend that needs no ydotool daemon, plus D-Bus activation for compositor shortcuts — [Vocalinux v0.18.0 release notes](https://newreleases.io/project/github/VocaHQ/vocalinux/release/v0.18.0). A Medium write-up covers installing it specifically on Debian — [Medium](https://medium.com/codex/talking-to-my-linux-box-without-talking-to-the-cloud-vocalinux-on-debian-without-the-tears-10bf053ea21b)
- whisrs: Rust daemon, supports Wayland, X11, Hyprland, Sway, GNOME, KDE; offline whisper.cpp or cloud backends; bills itself as the open-source Wispr Flow alternative for Linux — [whisrs on docs.rs](https://docs.rs/crate/whisrs/latest)
- Epicenter Whispering: runs on Linux/macOS/Windows, local and cloud engines; v7.5.0 added Parakeet local transcription and changed the Linux AppImage ("Added X11 dependencies and removed Wayland to fix compatibility issues") — [Epicenter v7.5.0 notes](https://newreleases.io/project/github/EpicenterHQ/epicenter/release/v7.5.0), [LinuxLinks](https://www.linuxlinks.com/whispering-speech-recognition-tool/)
- WhisperTux: small (77 stars), no tagged releases, last push April 2026 — [cjams/whispertux](https://github.com/cjams/whispertux)
- Newer entrants named in a 19 Nov 2026 It's FOSS round-up: **Myna** (Canonical-developed, snaps for Whisper/Parakeet/FunASR, targets Ubuntu 24.04+/26.04+, "under heavy development"), **TuxTalk** (Parakeet default, Whisper optional, understands spoken punctuation, hold F8 / tap F9, AppImage), **WhisPaste** (searchable history, DOCX export), **Hex** (note-taking oriented) — [It's FOSS](https://itsfoss.com/voice-typing-tools-linux/)
- Buzz and Vibe are file/recording transcription apps (batch transcription of audio files) rather than type-at-cursor dictation tools; both are actively maintained and MIT — [Buzz](https://github.com/chidiwilliams/buzz), [Vibe](https://github.com/thewh1teagle/vibe)

#### Talon Voice
- Talon does not support Wayland; its getting-started wiki tells users to select an X11 session — [Talon wiki mirror](https://www.github.com/Samikay/talonwiki/blob/main/getting_started.md)
- OSNews (31 May 2026) reports the developer's announcement: "Talon Voice will imminently remove ALL Linux support from the public release, as X11 continues to sunset..."; the article disputes the rationale and says KDE developers offered help that was declined. Removal was described as imminent, not confirmed shipped — [OSNews](https://www.osnews.com/story/145162/accessibility-input-tool-removes-x11-support-doesnt-want-to-support-wayland-users-caught-in-the-middle/)

#### Commercial tools
- **Superwhisper**: launched a Linux app (reported 5 Nov 2026), "built ... from scratch"; system-wide voice input on Wayland; officially supported distros: Omarchy, Arch, CachyOS, Fedora, Ubuntu, Debian, openSUSE; local (CPU/GPU) and cloud processing; GUI, TUI and CLI configuration; proprietary; free tier plus Pro — [AlternativeTo news](https://alternativeto.net/news/2026/11/superwhisper-launches-on-linux-for-seamless-voice-input-across-major-distributions/)
- **Wispr Flow**: official downloads page offers Mac (Apple Silicon/Intel), Windows and mobile; for Linux only "Vote to build for Linux" with a notify-me — [wisprflow.ai/downloads](https://wisprflow.ai/downloads). An Android app launched Feb 2026 — [TechCrunch](https://techcrunch.com/2026/02/23/wispr-flow-launches-an-android-app-for-ai-powered-dictation). A third-party page claiming "Linux beta support" is contradicted by the official page — [VoiceDash](https://voicedash.ai/wispr-flow-alternative/)
- **Aqua Voice**: Mac and Windows 10/11 only per a third-party comparison — [Laxis (vendor blog)](https://www.laxis.com/de/blog/wispr-flow-alternatives/)
- **Willow**: cloud-based, closed-source, "not available on Linux at all" — [Medium](https://medium.com/codex/talking-to-my-linux-box-without-talking-to-the-cloud-vocalinux-on-debian-without-the-tears-10bf053ea21b)
- **Dragon (Nuance/Microsoft)**: Dragon Professional v16 still sold at $699.99, Windows only, no major release since 2023; Dragon Home discontinued 2023; Dragon Dictate for Mac discontinued (2018); Dragon Anywhere mobile stopped selling 1 July 2026 — [Voibe review (competitor; no official Microsoft statement found)](https://www.getvoibe.com/resources/dragon-review/), [Voibe](https://www.getvoibe.com/resources/dragon-dictate-vs-dragon-naturallyspeaking/)
- Other proprietary tools with Linux builds: Spokenly (deb/rpm/AppImage) and Voicy (paid) — [Spokenly](https://spokenly.app/linux), [Voicy](https://usevoicy.com/blog/wispr-flow-alternative-for-linux)

### Inferences
- For this user (Debian 12, glibc 2.36, GNOME Wayland, 4 GB VRAM), the adoptable shortlist is: **Handy** (.deb/AppImage; needs ydotool or dotool on GNOME Wayland), **Speech Note** (Flatpak sidesteps glibc; has its own text buffer; heavy CUDA add-on), **hyprwhspr** and **Vocalinux** (Python, explicitly list Debian), and **Superwhisper** if proprietary is acceptable. voxtype's prebuilt binaries are ruled out by glibc; whisper-writer, WhisperTux and nerd-dictation are stale or tiny.
- Every one of these tools is designed for short utterances pasted at a cursor (messages, prompts, code comments). None is designed around the long-form book workflow (hours of continuous dictation, retained audio, session transcripts, a separate revision pass). hyprwhspr's "long-form mode" and Speech Note's notepad are the closest. That is the gap a custom "stenographer" would fill.
- Spanish is covered by every Whisper-based tool and by Parakeet V3 (multilingual); the choice of tool does not restrict the language, the choice of model does. Avoid English-only defaults (Parakeet V2, Hex's default, Moonshine English models).
- Maintenance signal is strong for Handy, voxtype, hyprwhspr, OpenWhispr, Vocalinux, Speech Note (all pushed within days of 2026-11-23), and Handy's ~40k stars makes it the de-facto reference implementation.
- Talon is not a viable basis for a new Linux workflow in late 2026.

### Gaps
- Not verified from official pages: MacWhisper (believed macOS-only), Aqua Voice and Willow platform lists (only third-party blogs seen), and Superwhisper's package format, local model list, X11 support, and whether it runs on Debian 12 specifically (vs. Debian 13).
- No independent accuracy benchmark comparing these apps in Spanish was found; Spanish quality evidence is one anecdotal HN comment plus the known properties of the underlying models (covered by the ASR-model researcher).
- Epicenter's licence: GitHub API reports no standard SPDX id; third-party listings say MIT. Not resolved.
- Whether Talon's Linux removal has actually shipped was not confirmed.
- No official Microsoft/Nuance statement on Dragon's roadmap was found; Dragon status comes from a competitor's site.
- OpenWhispr's X11/Wayland paste mechanism on Linux is not documented in its README.

---

## 2. What do authors who dictate books actually use and recommend?

### Takeaway
The long-standing author playbook is Dragon Professional (Windows) used either live or, more often among prolific authors, "record on a handheld recorder/phone while walking, then transcribe" (by Dragon's transcribe feature or a human typist); the consistently reported lessons are that dictation is a learned skill, that you speak punctuation, that drafting must be separated from editing, and that self-reported speeds run about 3,500–4,000+ words/hour versus ~2,000 typing. That "record now, transcribe later, then revise the transcript" workflow maps exactly onto a local-Whisper stenographer tool.

### Cited Findings
- Kevin J. Anderson has dictated for roughly 25 years, recording first drafts on a handheld recorder while hiking and having them transcribed; he has written a book on it, *On Being a Dictator* — [KJA blog](https://kjablog.com/on-being-a-dictator/), [MIT Press Bookstore listing](https://mitpressbookstore.mit.edu/book/9781680577501)
- He is profiled as a user of an Olympus/OM System DS-series professional dictation recorder — [OM System](https://dictation.omsystem.com/en/new-york-times-bestselling-author-turns-to-ds-3500); Kindlepreneur cites him as an author who dictates and uses a transcription service — [Kindlepreneur](https://kindlepreneur.com/how-to-dictate/)
- Kindlepreneur (updated 8 Nov 2025) describes three workflows: (1) live dictation at the computer; (2) record away from the desk, then auto-transcribe with Dragon Professional Individual (Dragon Home lacks this feature); (3) record and send audio to a human transcriptionist (costs money, higher accuracy, no need to speak punctuation) — [Kindlepreneur](https://kindlepreneur.com/how-to-dictate/)
- Kindlepreneur on punctuation: saying punctuation aloud "feels awkward at first" but becomes natural quickly — [Kindlepreneur](https://kindlepreneur.com/how-to-dictate/)
- Kindlepreneur on editing: expect extra editing at first; limit corrections during early sessions to a few minutes; if editing time cancels out drafting gains, check microphone and setup first; "poor audio quality leads to poorer transcription" — [Kindlepreneur](https://kindlepreneur.com/how-to-dictate/)
- Kindlepreneur on vocabulary: add unusual names by spelling then speaking them; correct via the software so it learns — [Kindlepreneur](https://kindlepreneur.com/how-to-dictate/)
- Monica Leonelle (*Dictate Your Book*) reports switching to dictation in 2013 raised her output from ~2,000 words/hour to "3500-4000+ words per hour"; her book description cites 4,000+ words/hour from "Walk 'n Talks" — [Leonelle's Substack](https://theworldneedsyourpassion.substack.com/p/introduction-to-dictation), [Audible listing](https://www.audible.com/pd/Dictate-Your-Book-How-to-Write-Your-Book-Faster-Better-and-Smarter-Audiobook/B01A63MN6Y)
- A 2016 review reports Leonelle claims 98% accuracy and a doubling of peak speed from 2,000 to 4,000 words/hour (self-reported) — [TeleRead](https://teleread.org/2016/08/11/dictate-your-next-book-a-few-tips/)
- Joanna Penn (The Creative Penn) has a standing guide and interviews on dictation (incl. the 2015 Leonelle interview and a 2018 "healthy writer" dictation-tips post); the site itself flags older posts as technically out of date — [Creative Penn: how to dictate your book](https://www.thecreativepenn.com/how-to-dictate-your-book/), [Creative Penn / Leonelle interview](https://www.thecreativepenn.com/2015/11/02/dictate-your-book-monica-leonelle/)
- Dragon availability has narrowed to one $699.99 Windows product (see section 1), which removes the traditional author tool for Mac and never existed for Linux — [Voibe (competitor)](https://www.getvoibe.com/resources/dragon-review/)
- A 2026 developer write-up describes replacing Wispr Flow with an offline Whisper setup on Linux — [vikrampawar blog](https://vikrampawar.github.io/2026/01/08/offline-voice-dictation-linux-whisper.html)

### Inferences
- The authors with the highest claimed output (Anderson, Leonelle) do **not** watch text appear while speaking. They record, walk, and transcribe later. This argues against prioritising real-time streaming display in the tool, and for: reliable capture, keep-the-audio, batch transcription with the best model that fits in 4 GB VRAM, then a separate revision surface.
- Modern Whisper-class models insert punctuation automatically, so the classic "speak your punctuation" discipline is less necessary than under Dragon; but paragraph breaks, dialogue marks (Spanish uses the raya —) and scene breaks are not inferred reliably, so a small set of spoken commands or an LLM formatting pass is still a design question for literary fiction.
- Human transcriptionists were valued because they (a) remove spoken punctuation and (b) tolerate messy speech; an LLM clean-up pass after ASR is the modern equivalent and is what Handy/voxtype/OpenWhispr expose as "post-processing".
- Words-per-hour figures are all self-reported by authors selling dictation books; treat 3,500–4,000 wph as an upper bound for fluent practitioners, not a baseline.

### Gaps
- Joanna Penn's own lessons (thecreativepenn.com returned HTTP 503 twice) are not captured in detail.
- No Spanish-language author accounts of dictating fiction were found; all sources are Anglophone indie-publishing authors.
- No systematic data on how long it takes to become fluent at dictating fiction; sources only say it takes practice.
- No sourced accounts of novelists using a phone voice memo + Whisper pipeline specifically, though it is the obvious successor to the recorder + Dragon-transcribe workflow.
- Scribe-style (interview-based ghostwriting) workflows were not researched.

---

## 3. Linux building blocks: audio capture, VAD, noise suppression, hotkeys, text injection

### Takeaway
Audio capture and VAD are solved problems on Linux (PipeWire with ALSA/Pulse compatibility; Silero VAD is the MIT-licensed default everyone uses); the hard, fragile part is system-wide hotkeys and text injection on Wayland, where no single mechanism works across compositors and GNOME in particular rejects `wtype`. A tool that owns its own text buffer (editor/TUI/local web app) avoids that whole problem class.

### Cited Findings

#### Audio capture
- sounddevice is a Python binding to PortAudio, available on Linux/macOS/Windows — [python-sounddevice](https://github.com/spatialaudio/python-sounddevice)
- PortAudio "exposes the lowest common API between all different platforms" and has no native PipeWire backend that apps can rely on; Mixxx ran a GSoC 2026 project to add direct PipeWire support for that reason — [Mixxx news](https://mixxx.org/news/2026-08-24-gsoc-2026-pipewire-support); a long-standing PipeWire issue discusses PortAudio using the existing ALSA/JACK backends — [PipeWire issue 130](https://gitlab.freedesktop.org/pipewire/pipewire/issues/130)
- `pipewire-pulse` lets PulseAudio applications use PipeWire as the server — [Debian wiki: PipeWire](https://wiki.debian.org/PipeWire)
- cpal (Rust): ALSA is required on Linux even when using JACK/PipeWire/PulseAudio; cpal 0.18 has an opt-in native PipeWire backend requiring `libpipewire-0.3-dev` — [cpal README](https://docs.rs/crate/cpal/0.18.0/source/README.md)
- whisrs uses cpal to open the default input at 16 kHz mono 16-bit on a dedicated thread (the cpal stream is not `Send`) — [whisrs capture.rs](https://docs.rs/crate/whisrs/0.1.5/source/src/audio/capture.rs)
- The user's machine has `pw-record` and `arecord` available **[local check]**, so a zero-dependency capture path is to spawn `pw-record --rate 16000 --channels 1 -` and read PCM from its stdout.

#### Voice activity detection
- Silero VAD: MIT, 10.7k stars, pushed 2026-11-23 — [snakers4/silero-vad](https://github.com/snakers4/silero-vad). Handy uses Silero to filter silence — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- A third-party review measured Silero ONNX at roughly 110x real time on a 60 s clip and relays maintainer-reported pure-noise accuracy of 0.87 for Silero v6 vs 0.42 for TEN VAD and 0 for WebRTC (not independently reproduced) — [Cekura](https://www.cekura.ai/blogs/what-is-silero-vad)
- TEN VAD claims better precision than Silero and WebRTC, faster speech-to-non-speech transition detection (says Silero lags "several hundred milliseconds"), and a smaller library (~306 KB vs ~2.2 MB) — vendor claims — [TEN VAD repo](https://github.com/TEN-framework/ten-vad), [PyPI](https://pypi.org/project/ten-vad/)
- TEN VAD's licence is Apache 2.0 with additional conditions (non-compete with Agora and restrictions on enabling third parties); GitHub reports it as non-standard — [Cekura](https://www.cekura.ai/blogs/what-is-silero-vad), [TEN-framework/ten-vad](https://github.com/TEN-framework/ten-vad)
- WebRTC VAD is BSD-3, the lightest, and the least accurate of the three in the available comparisons — [Cekura](https://www.cekura.ai/blogs/what-is-silero-vad), [Picovoice (competitor benchmark)](https://picovoice.ai/blog/best-voice-activity-detection-vad/)

#### Noise suppression
- Studies on speech-enhancement front ends generally find they do **not** help modern ASR: a medical-ASR study found "speech enhancement preprocessing degrades ASR performance across all noise conditions and models" — [arXiv 2512.17562](https://arxiv.org/abs/2512.17562v1); another reports denoising can reduce Whisper accuracy, with noisy originals recognised better than denoised versions — [arXiv 2502.13982](https://export.arxiv.org/pdf/2502.13982)
- DeepFilterNet is still maintained (pushed 2026-11-06, 5k stars) — [Rikorose/DeepFilterNet](https://github.com/Rikorose/DeepFilterNet); RNNoise and DeepFilterNet both appear as denoising baselines in RSA-Bench — [arXiv 2601.10384](https://arxiv.org/pdf/2601.10384)

#### Text injection and global hotkeys (X11 vs Wayland)
- `wtype` is the Wayland analogue of `xdotool type`, using the virtual-keyboard protocol; works only on compositors implementing it (Sway, Hyprland); fails on COSMIC — [COSMIC dictation write-up, Feb 2026](https://codeshrew.github.io/ai-lab-notes/posts/2026-02-11_voice-dictation-cosmic-wayland); does **not** work on GNOME or KDE — [scribe libei roadmap](https://perrette.github.io/scribe/roadmap-libei/); Handy's README confirms wtype fails on Ubuntu 26.04 GNOME Wayland — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- `ydotool` creates a virtual device through uinput below the compositor, so it works on both Wayland and X11, but needs the `ydotoold` daemon, correct socket ownership and `input`-group/uinput permissions; "not a 'seamless' backend" — [scribe roadmap](https://perrette.github.io/scribe/roadmap-libei/), [COSMIC write-up](https://codeshrew.github.io/ai-lab-notes/posts/2026-02-11_voice-dictation-cosmic-wayland). Upstream ydotool: AGPL-3.0, last push Dec 2025 — [ReimuNotMoe/ydotool](https://github.com/ReimuNotMoe/ydotool). Debian 12 packages the old 0.1.8 **[local check]**.
- `dotool` also uses uinput, works on X11 and Wayland, needs `input` group — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md); not packaged in Debian 12 **[local check]**
- libei (1.0 in mid-2023) is "the cross-compositor input-emulation protocol", reached through the XDG RemoteDesktop portal; works on GNOME Wayland and KDE Plasma 6.1+ and Hyprland; not on Sway/stock wlroots; first use per session shows a consent dialog ("control input devices"); token persistence depends on the xdg-desktop-portal version; events may be silently dropped on password fields — [scribe roadmap](https://perrette.github.io/scribe/roadmap-libei/). `wdotool` is an xdotool-like CLI using this path — [wdotool](https://github.com/cushycush/wdotool)
- Keystroke injection sends keycodes, so the result depends on the active xkb layout and takes 100+ keystrokes per utterance; for arbitrary Unicode the recommended pattern is "copy to clipboard, then inject only Ctrl+V / Shift+Insert" — [scribe roadmap](https://perrette.github.io/scribe/roadmap-libei/); Handy defaults to Shift+Insert paste on new Linux installs — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- Global hotkeys on Wayland: the `org.freedesktop.portal.GlobalShortcuts` portal exists — [portal docs](https://flatpak.github.io/xdg-desktop-portal/docs/_sources/doc-org.freedesktop.portal.GlobalShortcuts.rst.txt); backends exist on KDE Plasma 6+, GNOME 48+, Hyprland — [python-global-shortcut-portal](https://codeberg.org/marvin1099/python-global-shortcut-portal). Debian 12 ships GNOME 43, which predates that.
- The pragmatic patterns used by real tools: (a) bind a DE custom shortcut to a CLI command or signal that toggles the daemon (Handy `--toggle-transcription` / SIGUSR2; hyprwhspr `hyprwhspr record`; Vocalinux D-Bus activation); (b) read keys directly from evdev, needing `input` group (voxtype) — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md), [hyprwhspr README](https://raw.githubusercontent.com/goodroot/hyprwhspr/main/README.md), [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md), [Vocalinux v0.18.0](https://newreleases.io/project/github/VocaHQ/vocalinux/release/v0.18.0)
- "Recognition may succeed while the desktop blocks or misroutes the paste step" is described as the typical Wayland failure mode — [Spokenly (vendor)](https://spokenly.app/blog/speech-to-text-linux)

### Inferences
- On this user's exact environment (GNOME 43 on Wayland, Debian 12) system-wide injection is at its worst: wtype does not work on GNOME, the GlobalShortcuts portal backend is not there (GNOME 48+), Debian's ydotool is the old 0.1.8, and dotool must be built from source. Workable options are (1) build a current ydotool or dotool + uinput udev rule, (2) clipboard via `wl-copy` plus manual Ctrl+V, (3) log into an X11 session and use xdotool, or (4) do not inject at all.
- **A dedicated app that owns its text buffer is markedly simpler and fits the workflow better.** It needs no uinput permissions, no compositor-specific code, no clipboard clobbering, and no focus races; it also gives the things a book workflow wants and injection cannot: per-session audio retention, re-transcription with a better model later, timestamps linking text to audio, and a diff between raw transcript and revised fair copy. The hotkey problem reduces to an in-app key (or a GNOME custom shortcut calling a CLI toggle).
- A hybrid is cheap: own-buffer first, plus "copy session to clipboard" / write Markdown to the manuscript directory. System-wide typing can be bolted on later via the stdin→stdout hook pattern.
- Skip noise suppression in the ASR path by default; the research consensus is that Whisper-class models are trained on noisy audio and denoisers remove useful cues. Spend the effort on a close microphone and on VAD instead. If denoising is ever wanted, it should be A/B-tested on the user's own audio.
- VAD's role in a batch long-form tool is (a) trimming silence so Whisper does not hallucinate on quiet segments and (b) segmenting on pauses for chunked transcription; Silero (MIT, ONNX, CPU-cheap) is the obvious choice; TEN VAD's licence conditions are an unnecessary complication for a personal tool with no latency pressure.
- For capture, the PortAudio→ALSA→PipeWire route used by sounddevice is expected to work on Debian 12 but was not confirmed by a source; running `sounddevice.query_devices()` / `query_hostapis()` on the machine settles it. A `pw-record` subprocess is a dependable fallback.

### Gaps
- No source confirmed how sounddevice/PortAudio enumerates devices under PipeWire on Debian 12 specifically (pipewire-alsa vs. pipewire-pulse); needs a local test.
- miniaudio and Go audio libraries (malgo, portaudio-go) were not researched from primary sources.
- No direct RNNoise-vs-DeepFilterNet comparison as a Whisper front end was found.
- Independent (non-vendor) VAD benchmarks comparing Silero v6 and TEN VAD were not found.
- Whether libei/RemoteDesktop-portal injection works on GNOME 43 (Debian 12) was not verified; sources only state "GNOME Wayland (Ubuntu 24+)".
- No Arch Wiki page on dictation specifically was consulted.

---

## 4. Application frameworks for a custom tool: trade-offs

### Takeaway
Two proven stacks exist in the wild: Python (sounddevice/PipeWire + Silero + faster-whisper, as in hyprwhspr, Vocalinux, RealtimeSTT) for fastest iteration, and Rust (cpal + whisper.cpp/Parakeet bindings, Tauri UI, as in Handy, voxtype, whisrs) for a single distributable binary; a local web UI over a small local server is the lowest-friction way to get an owned text buffer.

### Cited Findings
- Python reference projects are active: faster-whisper (27k stars, MIT, pushed 2026-11-23) — [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper); RealtimeSTT (10.3k stars, Apache-2.0, pushed 2026-11-11) packages mic capture + VAD + faster-whisper — [KoljaB/RealtimeSTT](https://github.com/KoljaB/RealtimeSTT); `whisper_streaming` (3.7k stars, last push Nov 2025) implements the local-agreement streaming policy — [ufal/whisper_streaming](https://github.com/ufal/whisper_streaming)
- Python apps in production use: hyprwhspr, Vocalinux, Buzz, WhisperTux, whisper-writer are all Python — [hyprwhspr](https://github.com/goodroot/hyprwhspr), [Vocalinux](https://github.com/VocaHQ/vocalinux), [Buzz](https://github.com/chidiwilliams/buzz)
- Rust reference projects: Handy (Tauri app framework, Whisper via ggml, Silero VAD) — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md); voxtype (nine engines, ONNX engines behind Cargo features, CUDA/Vulkan builds) — [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md); whisrs (cpal capture at 16 kHz mono on a dedicated thread) — [whisrs](https://docs.rs/crate/whisrs/0.1.5/source/src/audio/capture.rs)
- Engine libraries: whisper.cpp (55k stars, MIT, pushed 2026-11-23) — [ggml-org/whisper.cpp](https://github.com/ggml-org/whisper.cpp); sherpa-onnx (16k stars, Apache-2.0, pushed 2026-11-23), which OpenWhispr uses for Parakeet — [k2-fsa/sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx), [OpenWhispr README](https://raw.githubusercontent.com/OpenWhispr/openwhispr/main/README.md)
- Electron is also viable: OpenWhispr (12k stars) is JavaScript/Electron driving whisper.cpp and sherpa-onnx — [OpenWhispr](https://github.com/OpenWhispr/openwhispr)
- Composability pattern common to Handy and voxtype: the transcript is piped through an arbitrary command (stdin→stdout) before output, which is where LLM clean-up attaches — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md), [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md)
- Prebuilt Rust binaries from other projects can be unusable on Debian 12 because of glibc (voxtype needs 2.38+) — [voxtype README](https://raw.githubusercontent.com/peteonrails/voxtype/main/README.md); Debian 12 has 2.36 **[local check]**

### Inferences
- **Python (sounddevice or pw-record + silero-vad + faster-whisper/CTranslate2 on CUDA)**: fastest path to a working tool; best ecosystem for models (Whisper variants, NeMo/Parakeet, onnx-asr); trivially scriptable LLM pass. Costs: virtualenv + CUDA/cuDNN wheel management on Debian 12, slower startup, GIL care around the audio callback (keep the callback to a queue push). Fits a single-user personal tool well.
- **Rust (cpal + whisper-rs / sherpa-rs / transcribe-rs, optional Tauri)**: one binary, low idle footprint, robust real-time audio threading; Handy can be forked or mined for patterns. Costs: slower iteration, C++ build dependencies (whisper.cpp with CUDA/Vulkan), WebKitGTK dependency for Tauri on Debian 12, cpal stream `!Send` ergonomics.
- **Go**: no prominent Go dictation tool surfaced in this research; audio and ASR would go through cgo bindings (PortAudio/miniaudio, whisper.cpp). Viable as an orchestrator (HTTP/WebSocket server, file management) around a whisper.cpp or faster-whisper server process, but offers the thinnest ecosystem of the three for ASR itself.
- **Browser UI + local server (getUserMedia/Web Audio → WebSocket → local ASR)**: gives an owned, rich text buffer (contenteditable/CodeMirror/ProseMirror), side-by-side raw transcript and fair copy, audio playback per paragraph, and works identically on X11 and Wayland with no injection; the browser handles mic permissions and device selection. Costs: browser audio processing (echo cancellation/AGC/noise suppression) should be disabled in getUserMedia constraints to avoid degrading ASR input; a tab must stay open; capture is tied to the browser rather than a background daemon. Alternatively the server captures audio itself (pw-record/sounddevice) and the browser is only the editor.
- **TUI**: simplest of all for a programmer (Textual/ratatui/bubbletea), integrates with a Markdown manuscript in git and with `$EDITOR`; weaker for prose revision with audio playback and diffing.
- Given the Dostoevsky-style workflow (dictate → transcript → author revises fair copy), latency is not a requirement, so the architecture can be a simple pipeline: record session to disk (FLAC/WAV) → VAD-segment → batch transcribe with the largest model that fits in 4 GB VRAM → optional LLM formatting pass → present the transcript for revision. That favours Python or a Go/Rust orchestrator around an ASR subprocess over a tightly integrated streaming design.

### Gaps
- No source directly compares these stacks for a dictation app; the trade-offs above are inference from what existing projects chose.
- Go ecosystem specifics (malgo, whisper.cpp Go bindings maturity in 2026) were not researched.
- Tauri 2 build requirements on Debian 12 (WebKitGTK 4.1 availability) were not verified.
- Performance of each engine on a GTX 1650 4 GB is out of scope here (ASR-model researcher).

---

## 5. Microphone hardware

### Takeaway
Distance to the mouth and signal-to-noise ratio matter far more than microphone price: the best hard evidence shows Whisper's error rate roughly doubling from headset to distant microphone on the same speech, while in a quiet room modern models do acceptably even on a laptop mic. A wired USB headset or a close USB mic is the cheap, safe choice; avoid Bluetooth headset-profile mics.

### Cited Findings
- Whisper large-v2: about 16.9% WER on AMI meetings recorded with individual headset mics vs about 36.4% on the same meetings from a single distant microphone (figures attributed to the original Whisper paper, relayed by a secondary source) — [Wispr Flow blog](https://wisprflow.ai/dictation-blogs/speech-to-text-how-it-works)
- Vendor claim: a $50 USB microphone "typically outperforms built-in laptop mics by 10-15 percentage points" (no methodology) — [Voicy](https://usevoicy.com/blog/voice-recognition-accuracy-comparison)
- Vendor claim: Whisper WER "climbs measurably when the signal-to-noise ratio drops below approximately 15 dB" (no methodology) — [Nuroum](https://nuroum.com/blog/flawless-ai-dictation-microphone-guide)
- Bluetooth: earbuds "can be slow to connect, clip your first word and produce more errors than wired options" — [Wispr Flow blog](https://wisprflow.ai/dictation-blogs/speech-to-text-how-it-works); telephone-grade 8 kHz audio can add 3–5 points of WER versus 16 kHz — [VoxBooster](https://voxbooster.com/blog/webcam-microphone-vs-headset-speech-quality-statistics-2026/); Handy documents that a Bluetooth headset mic degrades playback while recording (macOS) — [Handy README](https://raw.githubusercontent.com/cjpais/Handy/main/README.md)
- Counterpoint: "In a home office, private office, or hotel room, the best microphone for dictation is often the one already inside your laptop" — [Fireflies](https://fireflies.ai/blog/best-microphone-for-voice-dictation); "Modern speech recognition handles everyday speech well, even through a laptop mic in a quiet room" — [Elgato](https://www.elgato.com/eu/et/explorer/products/wave/choosing-a-microphone-for-ai-dictation/)
- A user report of a built-in laptop mic causing incorrect Whisper transcriptions — [LiveKit community](https://community.livekit.io/t/built-in-laptop-mic-causing-incorrect-whisper-transcriptions/1251)
- Author-side advice: choose the mic by where you dictate (desk vs walking); poor audio quality leads to poorer transcription; if editing cost is high, check the mic first — [Kindlepreneur](https://kindlepreneur.com/how-to-dictate/)
- Professional authors use dedicated dictation recorders (Olympus/OM System DS series) for walking dictation — [OM System](https://dictation.omsystem.com/en/new-york-times-bestselling-author-turns-to-ds-3500)
- A Nov 2026 arXiv paper proposes a failure taxonomy for streaming dictation ASR beyond WER — [arXiv 2611.16919](https://arxiv.org/pdf/2611.16919)

### Inferences
- Priority order for accuracy: (1) close-talking position (headset boom or a mic 10–20 cm from the mouth), (2) quiet room / high SNR, (3) wired USB or analog rather than Bluetooth HFP, (4) 16 kHz+ capture; microphone "quality tier" beyond that yields little for ASR. All ASR models downsample to 16 kHz mono anyway.
- For long literary dictation sessions, a headset keeps mouth-to-mic distance constant while the author moves, paces or turns away, which a desk condenser does not; a desk condenser also picks up keyboard, fans and room reverb.
- Mic quality "still matters" in the sense that distance/SNR still matter; it no longer matters in the Dragon-era sense of needing a certified noise-cancelling dictation headset for the engine to work at all.
- Because the tool keeps the audio, a mediocre mic is recoverable (re-transcribe later with a better model), but a distant, reverberant recording is not.

### Gaps
- No independent controlled study of headset vs. desk vs. laptop mic for single-speaker Whisper dictation was found; the AMI numbers are multi-speaker meetings and were not checked against the original paper.
- No trustworthy, current list of specific affordable mic models for dictation was captured: Kindlepreneur links out to a roundup without naming models, and the remaining sources are vendors (Nuroum, Elgato, Logitech) recommending their own products. Specific model recommendations and prices are therefore not provided.
- Nothing found on Spanish-specific acoustic considerations.

---

## 6. How Dostoevsky and Anna Snitkina worked on *The Gambler* (October 1866)

### Takeaway
Under a punitive contract with the publisher Stellovsky (deliver a new novel by 1 November 1866 Old Style or lose rights to his works for nine years), Dostoevsky hired the 20-year-old stenography student Anna Snitkina on 4 October (O.S.); for about 26 days he drafted notes on his own, dictated to her from roughly noon to four with tea breaks, she transcribed her shorthand into a clean longhand copy at home in the evenings, and the novel was finished at the end of October and delivered on the deadline. Dates differ between sources mainly because of Old Style vs. New Style calendars.

### Cited Findings
- Contract: Dostoevsky agreed to a "hazardous contract" with F. T. Stellovsky; if he did not deliver a novel of at least 12 signatures by 1 November 1866, Stellovsky gained the right to publish his works for nine years, until 1 November 1875, without compensation — [Wikipedia: The Gambler (novel)](https://en.wikipedia.org/wiki/The_Gambler_(novel)) (citing Malcolm Jones's OUP introduction and W. M. Todd's Penguin introduction)
- An alternative telling of the same contract: he sold collected-works rights for 3,000 rubles and owed a new novel "of at least 175 pages" by November 13 (i.e. 1 Nov O.S. in New Style), failing which rights would pass to Stellovsky "for perpetuity" — [The Marginalian](https://www.themarginalian.org/2016/02/15/anna-dostoyevsky-reminiscences-marriage/); the "perpetuity" wording conflicts with the nine-year term in [Wikipedia](https://en.wikipedia.org/wiki/The_Gambler_(novel))
- Through most of 1866 he was writing *Crime and Punishment* (then being serialised in *The Russian Messenger*) and had not started the contracted novel; he refused friends' offer to write portions for him — [The Marginalian](https://www.themarginalian.org/2016/02/15/anna-dostoyevsky-reminiscences-marriage/)
- Anna was recommended by her stenography teacher, Professor Olkhin; she had studied stenography for about half a year (about 150 enrolled, about 25 remained) — [Lit Hub excerpt of Andrew D. Kaufman, *The Gambler Wife*](https://lithub.com/once-dostoyevskys-stenographer-then-his-wife/)
- Start: she began work on 4 October 1866 (O.S.) — [Wikipedia: Anna Dostoevskaya](https://en.wikipedia.org/wiki/Anna_Dostoevskaya) (citing Lantz, *The Dostoevsky Encyclopedia*); The Marginalian gives the hiring as 15 October and her arrival next day at 11:30, which corresponds to New Style dating — [The Marginalian](https://www.themarginalian.org/2016/02/15/anna-dostoyevsky-reminiscences-marriage/)
- First meeting: he tested her by reading quickly from *The Russian Messenger*; she could not keep up and asked for conversational speed; he criticised an omitted full stop and an unclear hard sign, then asked her to return that evening to start dictating the novel — [Lit Hub / Kaufman](https://lithub.com/once-dostoyevskys-stenographer-then-his-wife/)
- Pace problem: "Dostoevsky initially dictated too fast"; once they settled into a rhythm they finished just in time — [Wikipedia: Anna Dostoevskaya](https://en.wikipedia.org/wiki/Anna_Dostoevskaya)
- Daily routine: for the next twenty-five days she came from noon to four; he dictated, she took stenographic notes, and transcribed them at home at night; sessions had short tea breaks with conversation — [The Marginalian](https://www.themarginalian.org/2016/02/15/anna-dostoyevsky-reminiscences-marriage/)
- He did not improvise entirely: he made rough sketches first, then dictated from 12 to 4 with short breaks to Snitkina, "who transcribed and copied it at home"; dictation ran 26 days, 4–29 October — [Hermitage Fine Art auction catalogue note](https://hermitagefineart.com/en/lots/2023-june-manuscripts/806/); "He wrote out parts of the story, then dictated them ... [she] transcribed them and made a clean copy" — [Wikipedia: The Gambler (novel)](https://en.wikipedia.org/wiki/The_Gambler_(novel))
- Method summarised as "Dictate → take shorthand → prepare the text" — [Govori with Nastya, citing Dostoevsky Museum chronology](https://govoriwithnastya.com/dostoevsky-the-gambler-26-days)
- Completion and delivery (sources differ by a day or two): last dictation 10 November N.S. (= 29 Oct O.S.), novel done in 26 days — [The Marginalian](https://www.themarginalian.org/2016/02/15/anna-dostoyevsky-reminiscences-marriage/); "On October 29th he completed The Gambler and sent it to Stellovsky" — [Lit Hub](https://lithub.com/dostoevsky-totally-did-nanowrimo/); finished 31 October and delivered on the deadline per a 2 November letter and the museum chronology — [Govori with Nastya](https://govoriwithnastya.com/dostoevsky-the-gambler-26-days); manuscript submitted 1 November 1866 — [Hermitage Fine Art](https://hermitagefineart.com/en/lots/2023-june-manuscripts/806/)
- He paid her 50 rubles for the work — [The Marginalian](https://www.themarginalian.org/2016/02/15/anna-dostoyevsky-reminiscences-marriage/)
- Aftermath: they became engaged about a month after starting and married 15 February 1867 — [Wikipedia: Anna Dostoevskaya](https://en.wikipedia.org/wiki/Anna_Dostoevskaya)
- First publication: *Igrok* appeared in vol. 3 of Stellovsky's Complete Works edition, St. Petersburg, 1866 — [Hermitage Fine Art](https://hermitagefineart.com/en/lots/2023-june-manuscripts/806/)
- Primary source for the daily routine is Anna Dostoevskaya's memoirs (*Dostoevsky: Reminiscences*, trans. Beatrice Stillman, 1975), listed as further reading — [Wikipedia: Anna Dostoevskaya](https://en.wikipedia.org/wiki/Anna_Dostoevskaya)

### Inferences
- Date discrepancies reconcile once calendars are aligned: 4 Oct O.S. = 16 Oct N.S.; 29 Oct O.S. = 10 Nov N.S.; 1 Nov O.S. = 13 Nov N.S. The Marginalian uses New Style; Wikipedia, the museum chronology and the auction note use Old Style. The remaining real disagreement is whether the text was finished on 29, 30 or 31 October (O.S.).
- The historical pipeline has four stages that map onto the tool: (1) author prepares notes/sketches alone beforehand (prompt/outline); (2) bounded afternoon dictation session, about four hours with breaks, at conversational speed (capture + ASR); (3) stenographer turns shorthand into a clean longhand copy overnight, off-line and not in real time (batch transcription + clean-up/formatting pass); (4) author receives a fair copy to work on (revision surface). The key design lesson is that transcription was asynchronous and that the stenographer produced a *clean copy*, not a raw verbatim one.
- The first-day anecdote (dictating too fast; complaints about a missing full stop) is a nice historical parallel for punctuation handling and for the speaker adapting pace to the transcriber.

### Gaps
- **The "next-day correction" step is not confirmed by any source fetched here.** The commonly repeated account (from Anna's *Reminiscences*) is that she brought the transcribed pages the next day, he read and corrected them before dictating further, and that they tracked the growing page count against the deadline; the sources retrieved confirm only dictation, overnight transcription and a clean copy. This should be checked directly in *Dostoevsky: Reminiscences* (Stillman translation, 1975) or Joseph Frank, *Dostoevsky: The Miraculous Years, 1865–1871* before being stated as fact.
- **The delivery anecdote is unverified and sources conflict.** The well-known version has Stellovsky absent to prevent delivery and the manuscript being lodged with a police station against a receipt on the eve of the deadline; one blog found in search instead says a notary, two hours before the deadline; neither was verified in a primary or scholarly source here.
- Joseph Frank's biography was not accessed; nothing in these notes is sourced to Frank.
- No direct quotations from Anna's memoir about the dictation process itself were retrieved (The Marginalian's memoir quotes concern their conversations and courtship).
- Anna's exact age (often given as 20) and the daily page counts were not sourced.
