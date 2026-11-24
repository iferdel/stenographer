# Local / open-source speech-to-text engines for long-form book dictation (state as of November 2026)

Target hardware for all "fits / does not fit" judgements: Debian 12, GTX 1650 (4 GB VRAM), 12 CPU threads, ~14 GB RAM. Primary language Spanish, secondary English. Research date: 2026-11-23.

Conventions: WER figures are as reported by each source; test sets, normalisation and dataset versions differ between sources, so cross-source comparisons are approximate. "RTFx" = seconds of audio processed per second of compute (higher is faster); "RTF" = the inverse (lower is faster).

---

## 1. What are the leading open ASR models in 2026 and how do they compare?

### Takeaway
The top of the English Open ASR Leaderboard is now dominated by large speech-LLMs (NVIDIA Nemotron 3.5 Transcribe, Qwen3-ASR, IBM Granite Speech, Cohere Transcribe, Canary-Qwen) that are irrelevant to a 4 GB GPU; Whisper large-v3 has fallen to roughly 41st of 61 but remains the most widely supported. The models that matter for this hardware are the small ones: Whisper large-v3-turbo (809 M, MIT), NVIDIA Parakeet-TDT-0.6b-v3 (600 M, CC-BY-4.0, Spanish included), NVIDIA Nemotron 3.5 ASR Streaming 0.6b (600 M, June 2026, true streaming, Spanish included), Canary-1b-v2 (978 M), and Moonshine streaming models (34 M to 245 M, MIT, Spanish available).

### Cited Findings

**Leaderboard snapshot (English average WER, Open ASR Leaderboard, read 29 Oct 2026, as reported by a secondary source)**
- Nemotron 3.5 Transcribe 30B-A4B: 5.33% avg WER, RTFx 462, released 28 Oct 2026, 34 B total / ~4.3 B active parameters, needs one H100 80 GB (BF16) or an RTX 5090 (NVFP4), OpenMDW-1.1 licence, no streaming, 40 languages. Ranked 9th of 61 overall (the entries above it are presumably closed/API models). — [Apidog, 17 Nov 2026](https://apidog.com/blog/best-open-source-speech-to-text-models/)
- Same snapshot: Qwen3-ASR-1.7B 5.40% (RTFx 819); IBM Granite Speech 5.0 2B 5.68% (RTFx 545); Cohere Transcribe (03-2026) 5.77% (RTFx 902); TheStage AI Whisper large-v3-turbo 5.91% (RTFx 1,177); NVIDIA Canary-Qwen 2.5B 5.94% (RTFx 862); NVIDIA Parakeet TDT 0.6B 5.98% to 6.18%; Mistral Voxtral Small 24B 6.38%; OpenAI Whisper large-v3 7.16%. — [Apidog, 17 Nov 2026](https://apidog.com/blog/best-open-source-speech-to-text-models/)
- Whisper large-v3 is described as 41st on the leaderboard, i.e. no longer near the top for raw accuracy, though an October 2026 AssemblyAI guide still calls it the most versatile general transcription option. — [Apidog](https://apidog.com/blog/best-open-source-speech-to-text-models/); [AssemblyAI](https://www.assemblyai.com/blog/top-open-source-stt-options-for-voice-applications)
- Sources conflict on leaderboard numbers by snapshot date: other 2026 snapshots give Cohere Transcribe 5.42%, Qwen3-ASR-1.7B 5.76%, Granite Speech 4.1 2B 5.33%, Canary-Qwen 2.5B 5.63%. — [VentureBeat](https://venturebeat.com/orchestration/coheres-open-weight-asr-model-hits-5-4-word-error-rate-low-enough-to-replace); [MarkTechPost, 23 Jul 2026](https://www.marktechpost.com/2026/07/23/best-open-speech-recognition-asr-models-in-2026-wer-languages-latency-and-license-compared/); [Gladia](https://www.gladia.io/blog/best-open-source-speech-to-text-models)
- Sources also conflict on Nemotron 3.5 Transcribe's size: "34B-parameter" vs "30B mixture-of-experts with ~4B active". — [NVIDIA research page](https://research.nvidia.com/labs/nemotron/NVIDIA-Nemotron-3.5-Transcribe/); [tech-insider](https://tech-insider.org/nvidia-nemotron-3-5-transcribe-open-weight-40-languages-2026/)
- The Open ASR Leaderboard multilingual track evaluates German, French, Italian, Spanish and Portuguese, on FLEURS, Common Voice / CoVoST-2 and MLS; a long-form track also exists. Paper counts are as of 27 March 2026. — [Open ASR Leaderboard paper, arXiv 2510.06961](https://arxiv.org/html/2510.06961v4); [GitHub repo](https://github.com/huggingface/open_asr_leaderboard)

**OpenAI Whisper large-v3-turbo** (older: released Oct 2024, still current; no newer open Whisper was found)
- 809 M parameters; decoder pruned from 32 layers (large-v3) to 4; "way faster, at the expense of a minor quality degradation"; MIT licence; 99 languages. — [HF model card](https://huggingface.co/openai/whisper-large-v3-turbo)
- Model-card evaluation: mean WER 7.83 on the Open ASR Leaderboard (English), RTFx 200.19. — [HF model card](https://huggingface.co/openai/whisper-large-v3-turbo)

**NVIDIA Parakeet-TDT-0.6b-v3** (older: released 14 Aug 2025)
- 600 M parameters, 25 European languages including Spanish and English, CC-BY-4.0, automatic punctuation and capitalisation, word/segment timestamps. — [HF model card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- So yes: v3 supports Spanish. (v2 is the English-only predecessor; sherpa-onnx lists `parakeet-tdt-0.6b-v2-int8` as English.) — [HF model card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3); [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)

**NVIDIA Canary-1b-v2** (older: released 14 Aug 2025)
- 978 M parameters, 25 European languages incl. Spanish and English, CC-BY-4.0, ASR plus speech translation, punctuation and capitalisation, word and segment timestamps, RTFx 749 and mean WER 7.15% on the (English) Open ASR Leaderboard, "at least 6GB RAM for model to load". — [HF model card](https://huggingface.co/nvidia/canary-1b-v2)

**NVIDIA Nemotron 3.5 ASR Streaming 0.6b** (new in 2026: released 4 Jun 2026)
- 600 M parameters; cache-aware FastConformer encoder (24 layers) + RNN-T decoder; 40 language-locales, of which 19 are "transcription-ready" including Spanish (es-US, es-ES) and English (en-US, en-GB); OpenMDW-1.1 licence, "ready for commercial use"; built-in punctuation and capitalisation; language given by `target_lang` or `auto`. — [HF model card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
- Runtimes named: NeMo 26.06, Transformers >= 5.13.0, and NeMo-Speech.cpp (GGUF, q8_0 quantisation). — [HF model card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
- The card recommends the separate English-only Nemotron ASR Streaming model for English-only use. — [HF model card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)

**Mistral Voxtral (Transcribe 2, Feb 2026)**
- Voxtral Mini 4B Realtime 2602: launched 4 Feb 2026 as part of Voxtral Transcribe 2; ~4 B parameters (~3.4 B LLM + ~970 M audio encoder); natively streaming; 13 languages including Spanish; Apache 2.0; BF16 weights only. — [HF model card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602); [arXiv 2602.11298](https://arxiv.org/abs/2602.11298)
- Requires "a single GPU with >= 16GB memory" via vLLM (recommended runtime); also Transformers >= 5.2.0, community pure-C (voxtral.c), MLX and Rust ports; llama.cpp not supported per the card; the Hub lists 48 quantised derivatives (formats not described on the card). — [HF model card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)
- The offline counterpart "Voxtral Mini Transcribe 2.0" appears in the card's benchmark table as a comparison point. — [HF model card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)

**Kyutai STT** (older: 2025)
- `kyutai/stt-1b-en_fr`: ~1 B parameters, English and French only, 0.5 s delay, streaming, includes semantic VAD, outputs capitalisation and punctuation, CC-BY-4.0. `kyutai/stt-2.6b-en`: ~2.6 B parameters, English only, 2.5 s delay. No Spanish model is listed. — [HF model card](https://huggingface.co/kyutai/stt-1b-en_fr)

**Moonshine (Moonshine AI, formerly Useful Sensors)**
- Moonshine v2 (Feb 2026 paper) introduces an "ergodic streaming encoder" for latency-critical use. — [arXiv 2602.12241](https://arxiv.org/abs/2602.12241)
- Speech-to-text languages: English, Spanish, German, Mandarin, Japanese, Korean, Vietnamese, Tagalog, Ukrainian, Arabic. Linux supported (plus Python, JS/WASM, iOS, Android, macOS, Windows, Raspberry Pi). The repo claims "higher accuracy than Whisper Large V3" (pointing at the Open ASR Leaderboard; English). — [GitHub README](https://github.com/moonshine-ai/moonshine)
- Spanish models: Spanish Small Streaming 123 M parameters, 4.9% WER, MIT; Spanish Tiny Streaming 34 M parameters, 6.2% WER, MIT. English Medium Streaming 245 M parameters, 6.65% WER, MIT. There is no Spanish Medium streaming model listed. — [Moonshine docs: available models](https://moonshine-voice.readthedocs.io/en/latest/models/available-models/)

**Vosk** (older generation: Kaldi-based)
- `vosk-model-es-0.42`: 1.4 GB, Apache 2.0, WER 7.50 (Common Voice test), 10.05 (mTEDx), 5.84 (MLS). `vosk-model-small-es-0.42`: 39 MB, WER 16.02 / 16.72 / 11.21 on the same sets. — [Vosk models page](https://alphacephei.com/vosk/models)

**Other 2026 arrivals (large speech-LLMs)**
- Cohere Transcribe (03-2026): 2 B parameters, Apache 2.0 (but gated behind a contact-information agreement), 14 languages, no automatic language detection, timestamps or diarisation. — [HF blog](https://huggingface.co/blog/CohereLabs/cohere-transcribe-03-2026-release); [MarkTechPost](https://www.marktechpost.com/2026/07/23/best-open-speech-recognition-asr-models-in-2026-wer-languages-latency-and-license-compared/)
- Qwen3-ASR-1.7B and Qwen3-ASR-0.6B: 30 languages plus 22 Chinese dialects, Apache 2.0. — [Qwen3-ASR technical report](https://arxiv.org/html/2601.21337); [MarkTechPost](https://www.marktechpost.com/2026/07/23/best-open-speech-recognition-asr-models-in-2026-wer-languages-latency-and-license-compared/)
- IBM Granite Speech 4.1 (three variants) Apache 2.0; a later Granite Speech 5.0 2B appears in the Oct 2026 leaderboard snapshot. — [MarkTechPost](https://www.marktechpost.com/2026/07/23/best-open-speech-recognition-asr-models-in-2026-wer-languages-latency-and-license-compared/); [Apidog](https://apidog.com/blog/best-open-source-speech-to-text-models/)
- Mozilla DeepSpeech and Coqui STT are discontinued. — [AssemblyAI](https://www.assemblyai.com/blog/top-open-source-stt-options-for-voice-applications)

### Inferences
- For a 4 GB GPU the realistic shortlist is: Whisper large-v3-turbo (via faster-whisper or whisper.cpp), Parakeet-TDT-0.6b-v3, Nemotron 3.5 ASR Streaming 0.6b, Canary-1b-v2 (tight), Moonshine Spanish Small Streaming, and Vosk as a legacy fallback. The leaderboard-topping speech-LLMs (Nemotron 3.5 Transcribe, Voxtral Small 24B, Canary-Qwen 2.5B, Granite, Cohere 2B, Qwen3-ASR-1.7B) are either impossible or impractical here.
- The English leaderboard ranking is a poor guide for this project: differences among the top ten are under 1 point of WER on English, while the decisive criteria here are Spanish quality, 4 GB fit, streaming and punctuation.
- Kyutai STT can be excluded for the primary use case because it has no Spanish model.

### Gaps
- Hardware requirements of Qwen3-ASR-0.6B (a plausible 4 GB candidate) and whether Spanish is among its 30 languages were not confirmed; no source retrieved gave VRAM or Spanish WER.
- distil-whisper: not verified this session. Background knowledge (unverified, may be outdated) is that the distil-large-v3 / v3.5 checkpoints are English-only, which would make them unsuitable for Spanish; the only sourced fact is that faster-whisper supports `distil-large-v3` ([faster-whisper README](https://github.com/SYSTRAN/faster-whisper)).
- WhisperX (m-bain/whisperX) was not fetched; no current facts verified.
- The live Open ASR Leaderboard Space could not be read directly (JS app); all leaderboard numbers here are from secondary articles or model cards.

---

## 2. Which support Spanish well, and what Spanish WER do benchmarks report?

### Takeaway
On published Spanish benchmarks, the 600 M to 1 B NVIDIA models and Voxtral match or beat Whisper large-v3: Spanish WER is roughly 3 to 5% for all serious contenders (Voxtral Realtime 2.7 to 3.3% FLEURS, Parakeet v3 3.45% FLEURS, Canary-1b-v2 2.94% MLS, Nemotron streaming 4.1 to 4.9% FLEURS, Whisper large-v3 4.3 to 4.9% on CoVoST2/MLS). Spanish is one of the best-performing languages for every multilingual model, typically better than English on the same benchmark.

### Cited Findings

| Model | FLEURS es | MLS es | CoVoST2 / Common Voice es | Source |
|---|---|---|---|---|
| Voxtral Mini Transcribe 2.0 (offline) | 2.63 | n/a | n/a | [Voxtral Realtime card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602) |
| Voxtral Mini 4B Realtime, 2400 ms delay | 2.71 | n/a | n/a | same |
| Voxtral Mini 4B Realtime, 960 ms | 2.98 | n/a | n/a | same |
| Voxtral Mini 4B Realtime, 480 ms (recommended) | 3.31 | n/a | n/a | same |
| Voxtral Mini 4B Realtime, 240 ms / 160 ms | 4.59 / 5.34 | n/a | n/a | same |
| Parakeet-TDT-0.6b-v3 | 3.45 | 4.39 | 3.41 | [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) |
| Canary-1b-v2 | not retrieved | 2.94 | 3.81 | [NVIDIA paper arXiv 2509.14128](https://arxiv.org/pdf/2509.14128) (via search extract) |
| Voxtral-Mini-3B-2507 (older, 2025) | not retrieved | 3.85 | 4.23 | same |
| Whisper large-v3 | not retrieved | 4.89 | 4.32 | same |
| Nemotron 3.5 ASR Streaming 0.6b, LangID given | 4.87 (80 ms) / 4.64 (160 ms) / 4.39 (320 ms) / 4.26 (560 ms) / 4.11 (1.12 s) | n/a | n/a | [Nemotron streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b) |
| Nemotron 3.5 ASR Streaming 0.6b, auto language | 5.04 / 4.82 / 4.48 / 4.34 / 4.13 | n/a | n/a | same |
| Moonshine Spanish Small Streaming (123 M) | 4.9 (test set not identified in extract) | | | [Moonshine docs](https://moonshine-voice.readthedocs.io/en/latest/models/available-models/) |
| Moonshine Spanish Tiny Streaming (34 M) | 6.2 (test set not identified) | | | same |
| Vosk es-0.42 (1.4 GB) | n/a | 5.84 | 7.50 (CV) | [Vosk models](https://alphacephei.com/vosk/models) |
| Vosk small-es-0.42 (39 MB) | n/a | 11.21 | 16.02 (CV) | same |

- English for comparison: Parakeet v3 FLEURS en 4.85, CoVoST en 6.80; Voxtral Realtime FLEURS en 4.05 (2400 ms) / 4.34 (960 ms) / 4.90 (480 ms), offline Voxtral Mini Transcribe 2.0 3.32; Nemotron streaming FLEURS en 9.43 (80 ms) to 7.91 (1.12 s). — [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3); [Voxtral Realtime card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602); [Nemotron streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
- Parakeet v3 WERs are computed after removing punctuation and capitalisation, with greedy decoding and no external language model. Averages across all 25 languages are much worse than Spanish (FLEURS 11.97, MLS 7.83, CoVoST 11.98), i.e. Spanish is among its strongest languages. — [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- Canary-1b-v2 aggregate: 8.40% FLEURS (25 languages), 8.85% CoVoST (13 languages), 7.27% MLS (6 languages). — [Canary-1b-v2 card](https://huggingface.co/nvidia/canary-1b-v2)
- The Nemotron streaming card warns its WER/CER normalisation is imperfect and may inflate error rates; es-US and es-ES are pooled into one row. — [Nemotron streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
- Whisper large-v3-turbo zero-shot on Common Voice 17.0 Spanish: 6.91% WER (5.34% after a community fine-tune). This is a self-reported figure from a fine-tuner's model card, the only turbo-specific Spanish number found. — [adriszmar/whisper-large-v3-turbo-es](https://huggingface.co/adriszmar/whisper-large-v3-turbo-es)
- Community Spanish fine-tunes of Whisper large-v3 exist: zuazo/whisper-large-v3-es reports 4.93 WER on Common Voice 13 es; BuzzASR reports 3.67 WER on FLEURS es and 5.87 on Common Voice 25. — [zuazo/whisper-large-v3-es](https://huggingface.co/zuazo/whisper-large-v3-es); [BuzzASR/spanish](https://huggingface.co/BuzzASR/spanish)
- Nemotron 3.5 Transcribe (the 30B model) covers 40 languages with 13 rated "leading"; NVIDIA's seven-language comparison gives it 4.62% mean WER vs 6.49% for Qwen3-ASR. Spanish specifically was not confirmed. — [Apidog](https://apidog.com/blog/best-open-source-speech-to-text-models/)

### Inferences
- All benchmark audio here is read or prepared speech (FLEURS, MLS audiobooks, Common Voice), which is close to "single speaker dictating in a quiet room"; MLS (audiobook readings) is arguably the closest proxy for literary dictation. On MLS es the ordering is Canary-1b-v2 (2.94) < Voxtral-Mini-3B (3.85) < Parakeet v3 (4.39) < Whisper large-v3 (4.89) < Vosk big (5.84).
- Differences of about 1 WER point between Parakeet v3, Canary v2, Whisper large-v3 and Nemotron streaming are within what normalisation differences can produce; the practical differentiators are punctuation quality, hallucination behaviour, prompting and latency, not headline Spanish WER.
- These WERs ignore punctuation and casing, which matter a great deal for literary prose (dialogue dashes, inverted question/exclamation marks); none of the sources measured Spanish punctuation accuracy.
- Whisper large-v3-turbo is likely somewhat worse than large-v3 in Spanish (model card: "minor quality degradation"), but no head-to-head Spanish FLEURS/MLS figure for turbo was found.

### Gaps
- FLEURS Spanish WER for Whisper large-v3, large-v3-turbo and Canary-1b-v2: the NVIDIA paper has a FLEURS per-language table but it could not be parsed (PDF binary); not retrieved.
- Open ASR Leaderboard multilingual-track Spanish column for each model: live Space not readable in this session.
- No Spanish WER found for Qwen3-ASR, Cohere Transcribe, Granite Speech, Nemotron 3.5 Transcribe.
- Moonshine's Spanish WER test set and normalisation were not identified; the docs note streaming and legacy scores are not comparable.
- No source evaluates Latin American vs Peninsular Spanish separately, nor Spanish punctuation/casing accuracy, nor literary vocabulary.

---

## 3. Which fit in 4 GB VRAM or run acceptably on a 12-thread CPU, with what quantisation, and how fast?

### Takeaway
Whisper large-v3-turbo in CTranslate2 int8 (about 1.5 GB VRAM) or fp16 (about 2.5 GB) fits comfortably on a 4 GB card; full large-v3 fits only in int8 (about 2.9 GB) and fp16 (about 4.5 GB) does not. The 600 M NVIDIA transducers are the CPU champions: Parakeet-TDT-0.6b-v3 int8 ONNX (about 670 MB) runs roughly 18 to 30 times faster than real time on a desktop i7 CPU, so it does not need the GPU at all. Voxtral Realtime (>= 16 GB GPU) and all the speech-LLMs do not fit.

### Cited Findings

**faster-whisper / CTranslate2**
- large-v2, RTX 3070 Ti 8 GB, 13 min audio, beam 5: fp16 1m03s / 4525 MB VRAM; int8 59s / 2926 MB VRAM; batched (batch 8) fp16 17s / 6090 MB; batched int8 16s / 4500 MB. — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)
- small model on CPU (i7-12700K, 8 threads), same 13 min audio: fp32 2m37s / 2257 MB RAM; int8 1m42s / 1477 MB RAM; batched int8 51s / 3608 MB. — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)
- large-v3-turbo, community benchmark (GPU not named in the extract), beam 5: fp16 19.2 s with 2537 MB VRAM; int8 19.6 s with 1545 MB VRAM; same WER (1.919) for both. — [faster-whisper issue #1030](https://github.com/SYSTRAN/faster-whisper/issues/1030)
- large-v3, community benchmark: int8 52.6 s / 2953 MB VRAM vs fp16 52.0 s / 4521 MB VRAM, but int8 WER was higher (4.594 vs 2.883) in that test. — [HF discussion, deepdml/faster-whisper-large-v3-turbo-ct2](https://huggingface.co/deepdml/faster-whisper-large-v3-turbo-ct2/discussions/3)
- GPU execution needs cuBLAS and cuDNN 9 for CUDA 12 (current ctranslate2 supports only CUDA 12 + cuDNN 9; older pins: ctranslate2 3.24.0 for CUDA 11/cuDNN 8, 4.4.0 for CUDA 12/cuDNN 8); libraries can be pip-installed on Linux with `LD_LIBRARY_PATH` set; FFmpeg is not required (PyAV). MIT licence. — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)
- Any Transformers-format Whisper checkpoint (including Spanish fine-tunes) can be converted with `ct2-transformers-converter`. — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)

**whisper.cpp**
- Memory (disk / RAM): tiny 75 MiB / ~273 MB; base 142 MiB / ~388 MB; small 466 MiB / ~852 MB; medium 1.5 GiB / ~2.1 GB; large 2.9 GiB / ~3.9 GB. large-v3-turbo is a supported download target (no row in the memory table). — [whisper.cpp README](https://github.com/ggml-org/whisper.cpp)
- Integer quantisation supported (README example: Q5_0). Backends: CUDA (`-DGGML_CUDA=1`), Vulkan (`-DGGML_VULKAN=1`), OpenVINO (encoder on x86 CPUs / Intel GPUs), OpenBLAS, and others. MIT licence. — [whisper.cpp README](https://github.com/ggml-org/whisper.cpp)

**NVIDIA transducers**
- Parakeet-TDT-0.6b-v3: "at least 2GB RAM" to load. — [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- Parakeet v3 int8 ONNX total size about 671 MB (vs 2.5 GB unquantised); sherpa-onnx int8 export has a ~622 MB encoder. — [istupakov/parakeet-tdt-0.6b-v3-onnx](https://huggingface.co/istupakov/parakeet-tdt-0.6b-v3-onnx); [soniqo/Parakeet-TDT-v3-ONNX](https://huggingface.co/soniqo/Parakeet-TDT-v3-ONNX)
- Parakeet v3 int8 on CPU (i7-12700KF): about 29.7x real time in one run and 18.41x (RTF 0.054) in the project's own table, with accuracy matching FP32 (community project, self-reported). — [groxaxo/parakeet-tdt-0.6b-v3-fastapi-openai](https://github.com/groxaxo/parakeet-tdt-0.6b-v3-fastapi-openai)
- Parakeet v3 int8 under sherpa-onnx 1.13.8, single thread: median RTF 0.0364 on a 2-vCPU Xeon 2.2 GHz cloud VM, 0.0101 on Apple M1 (15 to 30 s utterances). — [arXiv 2611.03605](https://arxiv.org/pdf/2611.03605) (as extracted by search; attribution of this figure to this paper should be double-checked)
- Canary-1b-v2: "at least 6GB RAM for model to load"; WhisperLiveKit docs say a GPU is "strongly recommended" for Canary and CPU "works but is slow for a 1B-parameter model". — [Canary-1b-v2 card](https://huggingface.co/nvidia/canary-1b-v2); [WhisperLiveKit README](https://raw.githubusercontent.com/QuentinFuxa/WhisperLiveKit/main/README.md)
- Nemotron 3.5 ASR Streaming 0.6b: no VRAM figure published; supported GPU microarchitectures include Turing (the GTX 1650's generation); a GGUF q8_0 build runs through NeMo-Speech.cpp; on an H100 it serves ~240 concurrent streams at 80 ms chunks and ~2,400 at 1.12 s. — [Nemotron streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)

**Does not fit**
- Voxtral Mini 4B Realtime: >= 16 GB GPU memory, BF16 only officially. — [Voxtral Realtime card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)
- Nemotron 3.5 Transcribe: one H100 80 GB or RTX 5090 with NVFP4. — [Apidog](https://apidog.com/blog/best-open-source-speech-to-text-models/)

**Tiny models**
- Moonshine Spanish Small Streaming 123 M parameters, Tiny 34 M; toolkit runs on Linux and Raspberry Pi-class hardware. — [Moonshine docs](https://moonshine-voice.readthedocs.io/en/latest/models/available-models/); [GitHub README](https://github.com/moonshine-ai/moonshine)
- Vosk big Spanish model is 1.4 GB on disk; small is 39 MB. — [Vosk models](https://alphacephei.com/vosk/models)

### Inferences
Fit matrix for GTX 1650 4 GB / 12 threads / 14 GB RAM (derived from the cited figures; no source benchmarked a GTX 1650 directly):

| Engine | GPU 4 GB | CPU-only | Notes |
|---|---|---|---|
| Whisper large-v3-turbo, faster-whisper int8 or fp16 | Yes (about 1.5 to 2.5 GB) | Usable for batch, likely near or below real time with int8 | Best-supported option; leaves VRAM headroom for the desktop |
| Whisper large-v3, int8 | Yes but tight (about 2.9 GB); fp16 (about 4.5 GB) does not fit | Too slow for interactive use | One community test showed int8 hurting large-v3 WER |
| Whisper small / medium | Yes | small int8 is about 7.6x real time on 8 threads of an i7-12700K (13 min in 1m42s) | Lower Spanish accuracy than large |
| Parakeet-TDT-0.6b-v3 | Yes (0.6 B params) | Yes, about 18 to 30x real time int8 on a desktop i7 | CPU alone is enough; the 12-thread CPU here is probably slower than an i7-12700K but with a large margin |
| Nemotron 3.5 ASR Streaming 0.6b | Very likely (same size class; Turing listed) | Plausible via GGUF q8_0 / NeMo-Speech.cpp | No published memory or CPU numbers |
| Canary-1b-v2 | Probably (about 1 B params) but unverified | Slow | 6 GB RAM to load |
| Moonshine Spanish Small/Tiny Streaming | Trivial | Yes, designed for CPU/edge | |
| Vosk es-0.42 | n/a (CPU) | Yes | Legacy accuracy |
| Voxtral Mini 4B Realtime | No officially (>= 16 GB) | Unknown; community C and quantised ports exist | Would need unverified community quantisations |
| Kyutai STT | n/a | n/a | No Spanish |
| Nemotron 3.5 Transcribe, Voxtral Small 24B, Canary-Qwen, Granite, Cohere 2B | No | No | |

- The batched faster-whisper pipeline raises VRAM by about 1.5 GB over sequential (4500 MB at batch 8 int8 for large-v2), so on 4 GB batching large models is off the table; with turbo, a small batch may fit.
- The GTX 1650 shares its 4 GB with the desktop compositor if it drives the display, so real headroom is under 4 GB; int8 turbo (about 1.5 GB) is the safe choice.
- Debian 12 will need the proprietary NVIDIA driver plus CUDA 12 / cuDNN 9 user-space libraries (pip-installable) for faster-whisper on GPU; the CPU-only ONNX route for Parakeet avoids the CUDA stack entirely.

### Gaps
- No benchmark on a GTX 1650 or any 4 GB card was found for any engine; all speed figures come from other hardware.
- No measured peak RAM for Parakeet v3 under sherpa-onnx / onnx-asr on CPU.
- No memory or CPU real-time-factor numbers for Nemotron 3.5 ASR Streaming 0.6b, Canary-1b-v2 on small GPUs, or Moonshine Spanish models.
- CPU real-time factor for large-v3-turbo on a 12-thread CPU (faster-whisper int8 or whisper.cpp Q5) was not found.
- Whether any of the 48 quantised Voxtral Realtime derivatives runs in 4 GB VRAM with acceptable accuracy is unknown.

---

## 4. True streaming vs batch; pseudo-streaming techniques for Whisper

### Takeaway
True low-latency streaming with Spanish is offered natively by Nemotron 3.5 ASR Streaming 0.6b (80 ms to 1.12 s chunks), Voxtral Mini 4B Realtime (80 ms to 2.4 s delay, but too big for this machine) and Moonshine streaming models; Parakeet v3 has a chunked NeMo streaming script. Whisper is a 30-second-window batch model and is made to "stream" with wrappers: VAD-gated chunking (Silero), LocalAgreement-2 (ufal whisper_streaming, about 3.3 s latency), and the newer AlignAtt policy (ufal SimulStreaming), all bundled in WhisperLiveKit.

### Cited Findings

**Native streaming models**
- Nemotron 3.5 ASR Streaming 0.6b: cache-aware design caches encoder self-attention and convolution state so each 80 ms frame is processed once with no overlapping recomputation; chunk sizes 80 ms, 160 ms, 320 ms, 560 ms, 1.12 s via `att_context_size`; Spanish FLEURS WER degrades only from 4.11 (1.12 s) to 4.87 (80 ms). — [Nemotron streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
- Voxtral Mini 4B Realtime: delay configurable from 80 ms to 1200 ms in 80 ms steps, plus 2400 ms; 480 ms is the recommended "sweet spot"; each text token corresponds to 80 ms; throughput "exceeding 12.5 tokens/second" needed for real time; websocket Realtime API through vLLM. — [Voxtral Realtime card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)
- Kyutai STT: streaming with 0.5 s (stt-1b-en_fr) or 2.5 s (stt-2.6b-en) delay and a semantic VAD, but English/French only. — [Kyutai card](https://huggingface.co/kyutai/stt-1b-en_fr)
- Moonshine: toolkit "optimized for live streaming, with low latency by doing work while the user is still talking"; Spanish streaming models exist (Tiny, Small). — [GitHub README](https://github.com/moonshine-ai/moonshine); [Moonshine docs](https://moonshine-voice.readthedocs.io/en/latest/models/available-models/)
- Parakeet-TDT-0.6b-v3: the card provides a NeMo streaming inference script (example `chunk_secs=2`, `left_context_secs=10.0`), i.e. chunked/buffered streaming rather than a cache-aware design. — [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- Canary-1b-v2: streaming is not mentioned on the card; WhisperLiveKit wraps it with LocalAgreement only. — [Canary-1b-v2 card](https://huggingface.co/nvidia/canary-1b-v2); [WhisperLiveKit README](https://raw.githubusercontent.com/QuentinFuxa/WhisperLiveKit/main/README.md)
- Nemotron 3.5 Transcribe (30B) has no streaming. — [Apidog](https://apidog.com/blog/best-open-source-speech-to-text-models/)
- sherpa-onnx (Apache-2.0, ONNX Runtime, fully offline) supports both streaming and non-streaming ASR, Silero VAD, punctuation models, keyword spotting; C/C++/Python/Go/Rust and more APIs; Linux x64. Its listed streaming Zipformer models are zh/en/ko/fr; no Spanish-specific streaming model is named on the README (the list is explicitly partial). — [sherpa-onnx README](https://github.com/k2-fsa/sherpa-onnx)

**Pseudo-streaming Whisper**
- whisper_streaming (ufal): the LocalAgreement approach, confirming output only when consecutive hypotheses agree (LocalAgreement-2), with self-adaptive latency; the paper reports "high quality and 3.3 seconds latency on unsegmented long-form speech". Dated 2023. — [Turning Whisper into Real-Time Transcription System, arXiv 2307.14743](https://arxiv.org/html/2307.14743)
- SimulStreaming (ufal): the follow-on, using the AlignAtt policy instead of LocalAgreement (2025). — [WhisperLiveKit README](https://raw.githubusercontent.com/QuentinFuxa/WhisperLiveKit/main/README.md)
- WhisperLiveKit (Apache 2.0): bundles both policies (`--backend-policy simulstreaming` is the default; `localagreement` optional); backends faster-whisper, vanilla whisper, mlx-whisper, Voxtral (HF transformers, GPU; uses its own streaming policy), qwen3-streaming, FunASR SenseVoice, Canary-1b-v2 (LocalAgreement only), OpenAI API; includes VAD and a Voice Activity Controller, `--pause-segmentation-seconds` (default 5.0), `--buffer_trimming sentence|segment`, diarisation, OpenAI/Deepgram-compatible API. Parakeet and Nemotron are not listed as backends. Its benchmarks were run on an H100 and published as scatter plots (English and French), no numeric latency in the README. — [WhisperLiveKit README](https://raw.githubusercontent.com/QuentinFuxa/WhisperLiveKit/main/README.md)
- A third-party blog claims 200 to 800 ms first-word latency for WhisperLiveKit without a benchmark; treat as unverified. — [Skywork blog](https://skywork.ai/blog/whisperlivekit-the-ultimate-solution-for-real-time-speech-recognition/)
- whisper.cpp `whisper-stream`: real-time microphone transcription that "samples the audio every half a second and runs the transcription continuously" (example `--step 500 --length 5000 -t 8`); needs SDL2 build flag. — [whisper.cpp README](https://github.com/ggml-org/whisper.cpp)
- VAD chunking: faster-whisper integrates Silero VAD (`vad_filter=True`), by default removing silences longer than 2 s, tunable via `vad_parameters` (e.g. `min_silence_duration_ms=500`); VAD is on by default in the batched pipeline. whisper.cpp supports `--vad` with a separately downloaded Silero model (example `silero-v6.2.0`) and options for threshold, min speech/silence duration, max speech duration, padding, overlap. — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper); [whisper.cpp README](https://github.com/ggml-org/whisper.cpp)

### Inferences
- For book dictation the simplest robust architecture is "utterance-level" pseudo-streaming: Silero VAD detects end of a phrase or sentence, the finished segment is sent to a batch model (turbo on GPU or Parakeet v3 on CPU), and the text appears 0.5 to 2 s after the pause. This avoids the flicker/retraction of LocalAgreement and gives the model full sentence context, which benefits punctuation.
- If live word-by-word feedback is wanted, Nemotron 3.5 ASR Streaming 0.6b is the only verified model that is simultaneously (a) natively streaming, (b) Spanish "transcription-ready", (c) punctuated, and (d) small enough for this hardware; its Spanish WER at 1.12 s (4.11) is on par with offline Whisper large-v3 figures.
- A two-pass design is natural: a streaming model for on-screen feedback, then an offline re-transcription of the saved audio with the most accurate model that fits (e.g. Canary-1b-v2 or large-v3) for the final manuscript text.
- Running Whisper large-v3-turbo under LocalAgreement/AlignAtt on a GTX 1650 repeatedly re-decodes a growing buffer; this is computationally heavier than a cache-aware transducer and published benchmarks are only on H100s, so latency on this card is uncertain.

### Gaps
- RealtimeSTT (KoljaB) and WhisperLive (Collabora): not fetched this session; no current facts verified. Background understanding (unverified) is that both are VAD-gated faster-whisper wrappers (RealtimeSTT as a Python library with wake-word/VAD and a small "realtime" model for previews; WhisperLive as a client/server with faster-whisper/TensorRT backends); their maintenance status in late 2026 should be checked.
- No measured end-to-end latency for any Whisper streaming wrapper on 4 GB-class hardware.
- Whether sherpa-onnx ships an official export of Parakeet-TDT-0.6b-v3 or Nemotron 3.5 streaming was not confirmed from the README (only v2 int8 is listed there; v3 and Nemotron appear in third-party project descriptions and community ONNX exports exist on Hugging Face).

---

## 5. Punctuation, capitalisation, long-form audio, hallucinations on silence, custom vocabulary / prompting

### Takeaway
All the modern contenders emit punctuation and capitalisation natively (Whisper, Parakeet v3, Canary v2, Nemotron streaming, Kyutai); Vosk does not natively and needs a separate punctuation model. Whisper is the only family with easy free-text prompting for names and style, but it is also the family with documented hallucination and repetition problems, which VAD gating largely mitigates; transducer models (Parakeet/Nemotron) are structurally less prone to hallucinating on silence but have no simple prompt mechanism documented on their cards.

### Cited Findings

**Punctuation and capitalisation**
- Parakeet v3: automatic punctuation and capitalisation, plus word/segment timestamps. — [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- Canary-1b-v2: output includes punctuation and capitalisation; word- and segment-level timestamps. — [Canary-1b-v2 card](https://huggingface.co/nvidia/canary-1b-v2)
- Nemotron 3.5 ASR Streaming: built-in punctuation and capitalisation; in auto-language mode appends a tag such as `<en-US>` after terminal punctuation (removable with `strip_lang_tags=true`). — [Nemotron streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
- Kyutai STT: "produces transcripts with capitalization and punctuation". — [Kyutai card](https://huggingface.co/kyutai/stt-1b-en_fr)
- sherpa-onnx provides separate "add punctuation" models for engines that emit raw text. — [sherpa-onnx README](https://github.com/k2-fsa/sherpa-onnx)
- Reported WERs for Parakeet/Canary exclude punctuation and capitalisation errors, so punctuation quality is unmeasured in those tables. — [Canary-1b-v2 card](https://huggingface.co/nvidia/canary-1b-v2); [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)

**Long-form audio**
- Whisper (Transformers): two algorithms. Sequential (default; sliding 30 s window, conditions on previous text) is "up to 0.5% WER more accurate"; chunked (`chunk_length_s=30`) is faster for a single long file. — [whisper-large-v3-turbo card](https://huggingface.co/openai/whisper-large-v3-turbo)
- Parakeet v3: up to 24 minutes with full attention (on an A100 80 GB) or up to 3 hours with local attention. — [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- Canary-1b-v2: dynamic chunking with 1 s overlap, applied automatically for long single files; long-form WER 13.78% on Earnings-22 and 9.87% on This American Life (English, conversational). — [Canary-1b-v2 card](https://huggingface.co/nvidia/canary-1b-v2)
- Voxtral Realtime: default `--max-model-len` 131072 tokens is about 3 hours; a 1-hour session needs >= 45000; no theoretical limit. — [Voxtral Realtime card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)
- Kyutai STT: performs well on audio up to 2 hours without changes. — [Kyutai card](https://huggingface.co/kyutai/stt-1b-en_fr)
- Long-form mean WER (Open ASR long-form track, English): Nemotron 3.5 Transcribe 10.98% vs Parakeet-TDT-0.6b-v3 13.37%. — [Apidog](https://apidog.com/blog/best-open-source-speech-to-text-models/)

**Hallucinations and repetition**
- OpenAI's card: predictions "may include texts that are not actually spoken in the audio input (i.e. hallucination)", and the seq2seq design makes the model "prone to generating repetitive texts", mitigated but not eliminated by beam search and temperature scheduling. Decoding controls: temperature fallback, `condition_on_prev_tokens`, compression-ratio and log-prob thresholds, no-speech threshold. — [whisper-large-v3-turbo card](https://huggingface.co/openai/whisper-large-v3-turbo)
- `condition_on_previous_text` defaults to True in faster-whisper; it improves consistency but can cause error loops; turning it off is a commonly recommended fix for repetition/hallucination loops. — [DeepWiki faster-whisper advanced features](https://deepwiki.com/SYSTRAN/faster-whisper/8.2-advanced-features); [openai/whisper discussion #679](https://github.com/openai/whisper/discussions/679)
- Whisper treats a segment as silent when no-speech probability is high and average log-probability is low; VAD pre-filtering (Silero) removes non-speech before it reaches the model. — [openai/whisper discussion #679](https://github.com/openai/whisper/discussions/679); [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)
- Voxtral Realtime: temperature should be set to 0.0. — [Voxtral Realtime card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)

**Custom vocabulary / prompting**
- Whisper `initial_prompt` biases output towards given vocabulary/spellings, but "only applies to the first window"; if the special terms occur later, plain initial prompting is ineffective. — [HF forum: Adding custom vocabularies on Whisper](https://discuss.huggingface.co/t/adding-custom-vocabularies-on-whisper/29311)
- A `hotwords` mechanism (tokenised hotword string placed after the start-of-prompt token, i.e. re-injected each window rather than only at the start) was proposed for openai/whisper in PR 2070. — [openai/whisper PR 2070](https://github.com/openai/whisper/pull/2070)
- WhisperLiveKit exposes `--init-prompt`, `--static-init-prompt` (a prompt that "doesn't scroll", i.e. persists across the stream), `--max-context-tokens` (~448), and a per-session `context` parameter for terminology or names (Whisper-family and SimulStreaming backends). — [WhisperLiveKit README](https://raw.githubusercontent.com/QuentinFuxa/WhisperLiveKit/main/README.md)
- Nemotron 3.5 ASR Streaming card does not mention word boosting or custom vocabulary. — [Nemotron streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b)
- sherpa-onnx: hotword boosting with modified beam search is used by a third-party app listed on the README, indicating contextual biasing exists for transducer models in that runtime, though the README itself does not document it. — [sherpa-onnx README](https://github.com/k2-fsa/sherpa-onnx)
- Nemotron 3.5 Transcribe (30B) is described as "promptable transcription" (a speech LLM), but it does not fit this hardware. — [The New Stack](https://thenewstack.io/nvidia-nemotron-promptable-transcription/)
- Fine-tuning is the other route: Whisper fine-tunes on Spanish cut Common Voice WER from 6.91% to 5.34% for turbo, and converted fine-tunes run in faster-whisper. — [adriszmar/whisper-large-v3-turbo-es](https://huggingface.co/adriszmar/whisper-large-v3-turbo-es); [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)

### Inferences
- For a novel with invented or foreign character names (e.g. Russian names in a Spanish text), Whisper's prompt mechanism is the most accessible tool: a short static prompt containing the names, re-applied to every VAD segment, sidesteps the "first window only" limitation because each utterance is its own first window. With transducer models, the equivalent would be hotword boosting (runtime-dependent) or a post-processing replacement dictionary / LLM clean-up pass.
- With VAD-segmented dictation, `condition_on_previous_text=False` plus a static prompt is the low-risk Whisper configuration: it prevents error loops while keeping spelling bias. The cost is losing cross-segment style continuity.
- Hallucination on silence is mainly a Whisper (attention encoder-decoder) problem; frame-synchronous transducers (Parakeet TDT, Nemotron RNN-T) emit blanks on silence by design, so they are a safer default for open-mic, long-pause dictation. This is an architectural inference; no source in this session measured it for Spanish.
- Dictation sessions of hours are best handled as many short VAD-bounded utterances rather than one multi-hour file; every engine's long-form limit then becomes irrelevant, and audio can be archived for a later, more accurate offline pass.
- None of these models handle spoken punctuation commands ("coma", "punto y aparte", "abre comillas") as commands; they infer punctuation from prosody. Dictation-style commands would need a post-processing layer.

### Gaps
- No source assessed Spanish-specific punctuation behaviour (inverted marks, dialogue em-dashes/rayas, quotation style) for any model.
- faster-whisper's own `hotwords` parameter semantics and current defaults were not confirmed from primary documentation.
- Whether NeMo's word-boosting / context-biasing features (GPU-PB, phrase boosting) apply to Parakeet v3 and Nemotron 3.5 streaming was not verified.
- No comparative hallucination-rate measurements (silence, breathing, keyboard noise) across these models were found.
- Vosk's lack of native punctuation is background knowledge, not verified in this session.

---

## 6. Licences

### Takeaway
Everything on the practical shortlist is usable for a commercially published book: Whisper and its runtimes are MIT, Voxtral Realtime / Qwen3-ASR / Granite / Cohere / Vosk / sherpa-onnx / WhisperLiveKit are Apache 2.0, Parakeet v3 / Canary v2 / Kyutai are CC-BY-4.0 (attribution), and NVIDIA's 2026 Nemotron models use OpenMDW-1.1 (stated as commercial-use ready). The one non-commercial trap is Moonshine's legacy non-streaming non-English models (including the Spanish Base model).

### Cited Findings
- Whisper large-v3-turbo: MIT. — [HF model card](https://huggingface.co/openai/whisper-large-v3-turbo)
- faster-whisper: MIT. whisper.cpp: MIT. — [faster-whisper](https://github.com/SYSTRAN/faster-whisper); [whisper.cpp](https://github.com/ggml-org/whisper.cpp)
- Parakeet-TDT-0.6b-v3: CC-BY-4.0. Canary-1b-v2: CC-BY-4.0, "ready for commercial/non-commercial use". — [Parakeet v3 card](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3); [Canary-1b-v2 card](https://huggingface.co/nvidia/canary-1b-v2)
- Nemotron 3.5 ASR Streaming 0.6b and Nemotron 3.5 Transcribe: OpenMDW-1.1; the streaming card says "ready for commercial use". — [Nemotron streaming card](https://huggingface.co/nvidia/nemotron-3.5-asr-streaming-0.6b); [Apidog](https://apidog.com/blog/best-open-source-speech-to-text-models/)
- Voxtral Mini 4B Realtime 2602: Apache 2.0. — [HF model card](https://huggingface.co/mistralai/Voxtral-Mini-4B-Realtime-2602)
- Kyutai STT weights: CC-BY-4.0. — [Kyutai card](https://huggingface.co/kyutai/stt-1b-en_fr)
- Moonshine: toolkit MIT; models "MIT by default too, in every language and at every size", except "the legacy non-streaming models for languages other than English", which are under the non-commercial Moonshine Community License (e.g. the 58 M Spanish Base model, 4.33% WER, is "Community" licensed; Spanish Tiny/Small Streaming are MIT). — [Moonshine README](https://github.com/moonshine-ai/moonshine); [Moonshine docs](https://moonshine-voice.readthedocs.io/en/latest/models/available-models/)
- Vosk Spanish models: Apache 2.0. — [Vosk models](https://alphacephei.com/vosk/models)
- sherpa-onnx: Apache-2.0. — [sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx)
- WhisperLiveKit: Apache 2.0 (bundled backends keep their own model licences, e.g. SenseVoiceSmall's own licence, Canary CC-BY-4.0). — [WhisperLiveKit README](https://raw.githubusercontent.com/QuentinFuxa/WhisperLiveKit/main/README.md)
- Cohere Transcribe, Granite Speech 4.1, Qwen3-ASR: Apache 2.0 (Cohere's repo is gated behind a contact-information agreement). — [MarkTechPost](https://www.marktechpost.com/2026/07/23/best-open-speech-recognition-asr-models-in-2026-wer-languages-latency-and-license-compared/)

### Inferences
- Model licences govern the weights and software, not the transcribed text; a dictated manuscript is the author's own work under any of these licences. Licence choice therefore matters mainly if the author later distributes a tool built on the stack, in which case the Moonshine Community License models should be avoided and CC-BY models need attribution.
- OpenMDW-1.1 is a relatively new model-weights licence; NVIDIA's own card asserts commercial readiness, but its exact terms were not read in this session.

### Gaps
- OpenMDW-1.1 licence text was not reviewed.
- Licences of WhisperX, RealtimeSTT, WhisperLive, whisper_streaming, SimulStreaming and distil-whisper were not verified in this session.
- Licence of the Silero VAD model itself was not verified in this session.
