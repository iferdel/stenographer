# Cloud speech-to-text APIs for long-form book dictation (state as of 2026-11-23)

Reading notes for the writer:
- All prices are USD list / pay-as-you-go unless marked. "/h" = per hour of audio. Per-minute prices converted x60.
- Pages were fetched on 2026-11-23 and summarised by a fetch tool; where a figure came from an aggregator (Artificial Analysis, Pipecat benchmark, search snippet) rather than the vendor's own page, it is marked "(secondary)".
- The model landscape has moved a lot since 2025: the names in the original brief (gpt-4o-transcribe, Universal-Streaming, Scribe v1/v2, Voxtral Mini Transcribe v1/v2, Soniox v3/v4) are now mostly legacy or deprecated. Current names are given below.

## 1. What are the leading cloud STT APIs in late 2026, their current models and prices?

### Takeaway
Batch transcription from first-tier vendors now costs about $0.10-$0.30 per audio hour (Soniox $0.10, ElevenLabs Scribe v3 $0.20, AssemblyAI ~$0.21, Mistral Voxtral Mini Transcribe 3 $0.21, OpenAI gpt-transcribe $0.27, Deepgram Nova-3 $0.26-$0.31); hyperscaler legacy products (Google Chirp 3 ~$0.96/h) are the expensive outliers, and Groq-hosted Whisper is the floor at $0.04/h. Several models in the original brief are deprecated: OpenAI's whisper-1 / gpt-4o-transcribe / gpt-4o-mini-transcribe shut down on 2027-02-26, AssemblyAI Universal-Streaming and Universal-3.5 Pro are being replaced by the "AssemblyAI-STT-3.7" family, and Soniox v5 is removed on 2026-12-15.

### Cited Findings

**OpenAI**
- Pricing page lists: gpt-transcribe $0.0045/min ($0.27/h); gpt-4o-transcribe $0.006/min ($0.36/h; $2.50 in / $10 out per 1M tokens); gpt-4o-mini-transcribe $0.003/min ($0.18/h); gpt-4o-transcribe-diarize $0.006/min; Whisper $0.006/min ($0.36/h); gpt-live-transcribe (live transcription) $0.017/min ($1.02/h); gpt-realtime-whisper $0.017/min; gpt-realtime-translate $0.034/min — [OpenAI pricing](https://developers.openai.com/api/docs/pricing)
- gpt-transcribe is the recommended model for recorded speech; whisper-1, gpt-4o-transcribe, gpt-4o-mini-transcribe and gpt-4o-transcribe-diarize are deprecated and shut down on February 26, 2027; gpt-live-transcribe is the recommended realtime path — [OpenAI speech-to-text guide](https://developers.openai.com/api/docs/guides/speech-to-text)
- Full speech-to-speech realtime models (gpt-realtime-2.1 at $32/$64 per 1M audio tokens in/out; gpt-realtime-2.1-mini $10/$20) exist but are voice-agent models, not transcription-priced — [OpenAI pricing](https://developers.openai.com/api/docs/pricing)

**Deepgram**
- Pre-recorded: Nova-3 Monolingual $0.0043/min ($0.26/h) PAYG, $0.0036 Growth; Nova-3 Multilingual $0.0052/min ($0.31/h) PAYG, $0.0043 Growth; hosted Whisper Large $0.0048/min — [Deepgram pricing](https://deepgram.com/pricing)
- Streaming: Nova-3 Monolingual $0.0048/min ($0.29/h; was $0.0077); Nova-3 Multilingual $0.0058/min ($0.35/h; was $0.0092); Flux English $0.0065/min ($0.39/h); Flux Multilingual $0.0078/min ($0.47/h) — [Deepgram pricing](https://deepgram.com/pricing)
- Add-ons per minute: Keyterm Prompting $0.0013 (+$0.078/h), Redaction $0.0020, streaming diarization $0.0020; Smart Formatting included. $200 free credit, no expiry, no card — [Deepgram pricing](https://deepgram.com/pricing)
- Flux is the newest model on the pricing page; no "Nova-4" is listed. Nova-2 is "existing deployments only" — [Deepgram pricing](https://deepgram.com/pricing)

**AssemblyAI**
- Current flagship is "AssemblyAI-STT-3.7" (pre-recorded) with "AssemblyAI-STT-3.7-Realtime" / "-Realtime-Agent" for streaming. Universal-3.5 Pro is listed as deprecated ($0.21/h, routes to STT-3.7 after retirement); Universal-2 $0.15/h; Universal-Streaming (English and Multilingual) $0.15/h of session time, "replaced by AssemblyAI-STT-3.7-Realtime"; Universal-3.6 Pro Realtime $0.45/h base — [AssemblyAI pricing](https://www.assemblyai.com/pricing)
- Artificial Analysis lists AssemblyAI-STT-3.7, Universal-3.5 Pro and Universal-3 Pro all at $3.50 per 1,000 min ($0.21/h) and "Universal" at $2.50 per 1,000 min ($0.15/h) (secondary) — [Artificial Analysis STT](https://artificialanalysis.ai/speech-to-text)
- Add-ons: keyterms prompting +$0.05/h on pre-recorded STT-3.7 (up to 1,000 terms) and Universal-2 (up to 200 terms), included free on STT-3.7-Realtime (up to 100 terms); general prompting (beta) +$0.05/h; custom formatting +$0.03/h. $50 free credit — [AssemblyAI pricing](https://www.assemblyai.com/pricing)

**ElevenLabs Scribe**
- Scribe v3 and Scribe v2 (batch) $0.20/h; Scribe v3 Live and Scribe v2 Realtime $0.22/h; Scribe v1 no longer listed. Keyterm prompting +$0.05/h batch, +$0.08/h realtime; "transcript editing" +$0.07/h batch, +$0.12/h realtime — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
- Included hours by subscription: Free 4h30 batch / 2h30 realtime; Starter $6/mo 30h batch / 27h realtime; Creator $22/mo 110h / 100h (plan-to-row mapping was inferred by the fetch tool from table order; verify) — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
- Conflict: the Pipecat benchmark table (price-update dates June-September 2026) lists scribe_v2_realtime at $0.39/h, and Artificial Analysis lists Scribe v2 at $3.67/1,000 min ($0.22/h) vs. Scribe v3 at $3.33 ($0.20/h); the vendor page ($0.22 realtime / $0.20 batch) is the more current primary source — [Soniox benchmarks page](https://soniox.com/benchmarks); [Artificial Analysis STT](https://artificialanalysis.ai/speech-to-text)

**Mistral Voxtral**
- Voxtral 3 family, per audio minute: Voxtral Mini Transcribe 3 (batch) $0.0035/min ($0.21/h); Voxtral Small Transcribe 3 $0.004/min ($0.24/h); Voxtral Mini Transcribe Realtime 3 $0.008/min ($0.48/h); older Voxtral Mini Transcribe Realtime $0.006/min (secondary: search snippets citing a 2026-10-22 pricing-page snapshot; Mistral's own pricing page did not render rates) — [usagepricing.com snapshot](https://www.usagepricing.com/blueprint/activity/mistral-ai-2026-10-22-voxtral-3-audio-pricing); [fourweekmba](https://fourweekmba.com/ai-mistrals-voxtral-3-transcribes-speech-from-0-0035-a-minute/); [llmreference](https://www.llmreference.com/model/voxtral-mini-transcribe-realtime-3/mistral-ai-api)
- Artificial Analysis corroborates: Voxtral Small Transcribe 3 $4.00, Voxtral Mini Transcribe 3 $3.50, Voxtral Mini Transcribe 2 $3.00 per 1,000 min (secondary) — [Artificial Analysis STT](https://artificialanalysis.ai/speech-to-text)
- Mistral's pricing page only confirms "speech models are per minute" — [Mistral pricing](https://mistral.ai/pricing)

**Groq-hosted Whisper**
- whisper-large-v3-turbo $0.04/h (speed factor 216, Groq-stated WER 12%); whisper-large-v3 $0.111/h (speed factor 189, WER 10.3%). Minimum billed length 10 s per request. No streaming mentioned — [Groq speech-to-text docs](https://console.groq.com/docs/speech-to-text)

**Google**
- Chirp 3 is listed at $16.00 per 1,000 min ($0.96/h) and Gemini 3.5 Transcribe at $5.00 per 1,000 min ($0.30/h); Gemini 2.5 Flash Lite $0.67 and Gemini 3.1 Flash-Lite Preview $1.10 per 1,000 min are the cheap general-LLM routes (secondary) — [Artificial Analysis STT](https://artificialanalysis.ai/speech-to-text)
- OpenRouter lists Chirp 3 at $0.016/min; snapshots of Google's pricing page show $0.016/min standard for the first 500,000 min/month and a $0.003/min rate that appears to be dynamic batch (secondary; Google's own page did not render) — [OpenRouter Chirp 3](https://openrouter.ai/models/google/chirp-3); [Google STT pricing](https://cloud.google.com/speech-to-text/pricing/)
- gemini-3.5-transcribe-live is listed at $0.54/h in the Pipecat streaming benchmark table (secondary) — [Soniox benchmarks page](https://soniox.com/benchmarks)

**Microsoft Azure Speech / MAI**
- Azure pricing page lists categories Real-time, Fast Transcription, MAI Transcribe-2, MAI Transcribe-1.5, Batch, and "LLM Speech" (same SKU/price as Fast Transcription), but rates rendered as placeholders. Free F0 tier: 5 audio hours/month of real-time. MAI Transcribe-2 price is "a limited-time promotional offer through 12/31/2026" — [Azure Speech pricing](https://azure.microsoft.com/en-us/pricing/details/speech/)
- Artificial Analysis: MAI-Transcribe-2 $1.67 per 1,000 min ($0.10/h), MAI-Transcribe-1.5 $6.00, "Azure Speech 09-2026" $6.00 per 1,000 min ($0.36/h) (secondary) — [Artificial Analysis STT](https://artificialanalysis.ai/speech-to-text)
- Pipecat streaming table lists Azure real-time at $1.60/h (secondary) — [Soniox benchmarks page](https://soniox.com/benchmarks)

**AWS Transcribe**
- Page examples state batch $0.006/min ($0.36/h) and streaming $0.01/min ($0.60/h) in US East; free tier 60 min/month for 12 months. Tier tables did not render — [AWS Transcribe pricing](https://aws.amazon.com/transcribe/pricing/)
- Artificial Analysis lists Amazon Transcribe at $6.00 per 1,000 min, consistent with $0.006/min (secondary) — [Artificial Analysis STT](https://artificialanalysis.ai/speech-to-text)

**Speechmatics**
- Per hour, batch / real-time: Melia 1 $0.24 / $0.40; Oak 1 $0.30 / $0.46; Standard $0.45 / $0.45; Enhanced $0.75 / $0.80; Linden 1 real-time only $0.30 (promo, was $0.40). $100 free credit. Opt-in model-training programme gives 33% off (off by default) — [Speechmatics pricing](https://www.speechmatics.com/pricing)

**Soniox**
- Async $0.10/h, real-time $0.12/h. Token basis: input audio $1.50 (async) / $2.00 (RT) per 1M tokens; ~30,000 audio tokens per hour — [Soniox pricing](https://soniox.com/pricing)
- Current models stt-rt-v6 and stt-async-v6; v5 deprecated, removed 2026-12-15 and auto-routed to v6; 60+ languages — [Soniox models docs](https://docs.soniox.com/stt/models)

**Gladia**
- Self-serve (EUR): async Solaria-3 from EUR 0.16/h, async Solaria-1 from EUR 0.27/h, real-time EUR 0.68/h. EUR 50 free credit valid one year. Solaria-3 covers 5 languages; Solaria-1 covers 100+ — [Gladia pricing](https://www.gladia.io/pricing)

**Notable newcomers (from the Artificial Analysis table; all secondary)**
- xAI "Grok Voice Transcribe 2.0": AA-WER 2.3%, $1.67/1,000 min ($0.10/h). Microsoft "MAI-Transcribe-2": 2.0%, $1.67. Zoom "Scribe V2.1 Pro": 2.1%, $5.83. Cohere "transcribe-03-2026": 4.6%, listed $0.00. Smallest.ai Pulse / Pulse Pro: 3.3% / 3.4%, $3-$4. Inworld STT 1: 3.9%, $2.50. Reson8 Rumble-2: 2.7%, $22.25. Alibaba Fun-Realtime-ASR-preview: 1.7%, $2.82. NVIDIA Nemotron 3.5 Transcribe via DeepInfra: 3.4%, $2.00 — [Artificial Analysis STT](https://artificialanalysis.ai/speech-to-text)

### Inferences
- For a solo author the price differences among the top ~10 vendors are economically irrelevant (see section 6); selection should be driven by Spanish accuracy, dictation ergonomics and privacy terms.
- Anything built today on whisper-1 / gpt-4o-transcribe needs migrating before 2027-02-26; gpt-transcribe is both cheaper ($0.27/h vs $0.36/h) and the supported path.
- AssemblyAI STT-3.7 pre-recorded price is inferred as $0.21/h from Artificial Analysis plus the "Universal-3.5 Pro routes to STT-3.7" note; the vendor page extract did not state it directly.

### Gaps
- Mistral, Google Cloud STT and Azure prices could not be read from the vendors' own pages (JS-rendered / placeholders); figures above are from Artificial Analysis, OpenRouter and third-party snapshots and should be re-verified.
- AssemblyAI-STT-3.7-Realtime base price per hour was not captured (only Universal-3.6 Pro Realtime $0.45/h and legacy $0.15/h).
- Groq: did not confirm whether newer ASR models (beyond the two Whisper variants) are hosted; the Groq docs page lists only those two.
- No per-model price confirmation for Azure real-time ($1.60/h is from a third-party benchmark table and looks high vs. historical ~$1/h).

## 2. How accurate is each for Spanish? Which handle Latin American (e.g. Chilean) accents well?

### Takeaway
No independent Spanish-only leaderboard was found; the best per-language data is a vendor-run (AssemblyAI) streaming benchmark dated November 2026 in which most modern models land at roughly 3-8% WER on Spanish read speech, with OpenAI's older gpt-4o models and Deepgram Nova-3 clearly behind (12-15% on FLEURS-es). No source tested Chilean or other specific Latin American accents, so the author must test on their own voice.

### Cited Findings
- Artificial Analysis AA-WER v2.2 (English-centric: AA-AgentTalk 50%, VoxPopuli-Cleaned 25%, Earnings22-Cleaned 25%; ~8 h audio; no per-language/Spanish breakdown). Selected results: Alibaba Fun-Realtime-ASR-preview 1.7%; ElevenLabs Scribe v3 1.9%; MAI-Transcribe-2 2.0%; Voxtral Small Transcribe 3 2.1%; Zoom Scribe V2.1 Pro 2.1%; Scribe v2 2.2%; Voxtral Mini Transcribe 3 2.2%; Grok Voice Transcribe 2.0 2.3%; AssemblyAI-STT-3.7 2.5%; Gemini 3.5 Transcribe 2.6%; Azure Speech 09-2026 2.8%; OpenAI GPT Transcribe 3.3%; Gladia Solaria-3 3.2%; Soniox v5 Async 3.8%; GPT-4o Transcribe 4.0%; Speechmatics Enhanced 4.0%; Amazon Transcribe 4.1%; Whisper Large v2 (OpenAI) 4.1%; Chirp 3 4.3%; GPT-4o Mini Transcribe 4.5%; Groq Whisper Large v3 Turbo 4.6%; Speechmatics Melia 4.9%; Deepgram Nova-3 5.2% — [Artificial Analysis STT](https://artificialanalysis.ai/speech-to-text)
- AssemblyAI benchmark page (vendor-run; real-time page dated 2026-11-16; FLEURS runs 2026-08-25 to 2026-11-14; rivals tested via public streaming APIs at default settings; normalized WER). Spanish WER, FLEURS-es / Common Voice-es: Google Gemini 3.5 Live 6.0 / 4.0; ElevenLabs Scribe v3 Live 6.8 / 4.0; Soniox Realtime v6 6.9 / 5.3; AssemblyAI-STT-3.7-Realtime 7.5 / 2.9; AssemblyAI-STT-3.7-Realtime-Agent 7.3 / 2.8; AssemblyAI Universal-3.6 Pro 7.9 / 3.2; Speechmatics Enhanced 4.7 / 2.5; Speechmatics Standard 5.4 / 4.2; Mistral Voxtral Mini 4.8 / 5.7; xAI Grok Voice Transcribe 2.0 4.9 / 6.7; Zoom Scribe (Live) 5.2 / 5.7; Reson8 4.0 / 3.5; Gladia Solaria 6.7 / 7.8; Deepgram Flux 7.8 / 7.8; Meta Muse Voice Transcribe 9.5 / 4.9; OpenAI GPT Realtime 11.8 / 6.9; Azure 12.0 / 6.8; OpenAI GPT-4o Transcribe 12.1 / 8.9; OpenAI GPT-4o mini Transcribe 14.9 / 9.8; Deepgram Nova-3 15.0 / 7.7; AWS Transcribe - / 4.1; ElevenLabs Scribe v2 - / 5.8. CAUTION: these values were extracted by an automated reader from four very long tables (Tables 10-13) on a 296k-character page; row/column alignment was not manually verified and should be re-checked against the page before quoting — [AssemblyAI benchmarks](https://www.assemblyai.com/benchmarks)
- Same page, multilingual FLEURS average over 18 languages: AssemblyAI-STT-3.7-Realtime-Agent 7.35%, STT-3.7-Realtime 7.51% — [AssemblyAI benchmarks](https://www.assemblyai.com/benchmarks)
- ElevenLabs places Spanish in its "Excellent (<= 5% WER)" tier (based on the Scribe v2 breakdown) and states Scribe v3 has "27% fewer word errors than Scribe v2 on FLEURS"; Scribe v3 Live has "44% lower semantic WER than Scribe v2 Realtime on FLEURS" (vendor claims) — [ElevenLabs STT docs](https://elevenlabs.io/docs/overview/capabilities/speech-to-text)
- Pipecat STT streaming benchmark (English, 1,000 real-world samples, semantic WER judged by an LLM; page dated November 2026; hosted on Soniox's site): Soniox stt-rt-v6 0.74% mean WER; AssemblyAI universal-3-6-pro 0.89%; Azure 0.98%; Speechmatics linden-1 1.11%; AssemblyAI universal-3-5-pro 1.12%; AWS 1.26%; Deepgram nova-3-general 1.32%; Google gemini-3.5-transcribe-live 1.93%; OpenAI gpt-realtime-whisper 2.41%; ElevenLabs scribe_v2_realtime 3.05%; OpenAI gpt-4o-transcribe 3.10%. Differences under ~0.25 points among the top services are within the 95% CI. No Spanish breakdown — [Soniox benchmarks page](https://soniox.com/benchmarks)
- Gladia's benchmark page lists multilingual-aggregate Common Voice 24 results (AssemblyAI 3.9, Mistral Voxtral 5.1, Soniox v4 7.2) — not Spanish-only (vendor page, via search summary) — [Gladia benchmarks](https://www.gladia.io/competitors/benchmarks)
- Coval's English real-time leaderboard: Universal 3.6 Pro 2.2%, Scribe v2 Realtime 4.3%, Soniox STT RT v5 4.8%, Deepgram Nova 3 5.2%, Voxtral Mini Transcribe Realtime 5.3% (via search summary) — [Coval](https://www.coval.ai/blog/best-speech-to-text-providers-in-2026-independent-benchmarks-and-how-to-choose/)
- Groq's own docs state WER 12% for whisper-large-v3-turbo and 10.3% for whisper-large-v3 (dataset unspecified, not Spanish-specific) — [Groq speech-to-text docs](https://console.groq.com/docs/speech-to-text)
- Deepgram language codes: Nova-3 supports `es` and (monolingual) `es-419` (Latin American Spanish); legacy enhanced/base also `es-LATAM`; no Chile-specific code. Flux multilingual (`flux-general-multi`) covers en, es, fr, de, hi, ru, pt, ja, it, nl — [Deepgram models & languages](https://developers.deepgram.com/docs/models-languages-overview)
- Voxtral Mini Transcribe V2 lists Spanish among its 13 supported languages; Voxtral Realtime claims "strong performance in 13 languages" — [Mistral STT docs](https://docs.mistral.ai/capabilities/audio/speech_to_text/)
- Gladia Solaria-3 supports only 5 languages (list not captured); Solaria-1 supports 100+ — [Gladia pricing](https://www.gladia.io/pricing)

### Inferences
- On the available (vendor-run) Spanish numbers, the consistently strong group is Speechmatics Enhanced, ElevenLabs Scribe v3, Soniox v6, AssemblyAI STT-3.7, Google Gemini 3.5 transcribe/live, Mistral Voxtral 3 and xAI Grok Voice Transcribe; the consistently weak group for Spanish is OpenAI gpt-4o-transcribe / mini and Deepgram Nova-3. OpenAI's newer gpt-transcribe was not in the Spanish table, so its Spanish standing is unknown.
- FLEURS and Common Voice Spanish are read speech with mixed Peninsular and Latin American speakers; they are a reasonable proxy for a single speaker in a quiet room but do not isolate Chilean Spanish (aspirated/elided /s/, fast rate, voseo forms like "cachai"), which is a known hard case. Vendor rankings swap between FLEURS and Common Voice (e.g. AssemblyAI 7.5 vs 2.9; Voxtral 4.8 vs 5.7), so differences of 1-3 points should not be over-read.
- Clean single-speaker dictation is the easiest ASR condition; real-world WER for the author will probably be lower than these benchmark numbers for every top-tier vendor, and proper nouns/invented words (addressed by keyterms) will dominate the residual errors.

### Gaps
- No independent, Spanish-only, 2026 benchmark covering all vendors was found. Artificial Analysis publishes no per-language data; the Hugging Face Open ASR Leaderboard was not checked.
- No benchmark at all on Chilean or other regional Latin American accents for any vendor. Only Deepgram exposes an explicit Latin American locale (`es-419`); whether it helps Chilean speech is untested.
- Spanish numbers for batch (pre-recorded) models — AssemblyAI's pre-recorded tab, Scribe v3 batch, gpt-transcribe, Voxtral Small Transcribe 3, Soniox async v6 — were not captured.
- The AssemblyAI Spanish table needs manual verification (automated extraction; some rows list models in unexpected order).

## 3. Which offer real-time streaming with partial results, at what latency, and at what price vs. batch?

### Takeaway
Nearly every vendor now has a streaming endpoint; time-to-final-transcript after end of speech is roughly 250-500 ms for the specialists (Deepgram, Soniox, AssemblyAI, ElevenLabs, Speechmatics) and 0.6-1.1 s for OpenAI, Google legacy, Azure and AWS. Streaming premiums range from negligible (Soniox +20%, ElevenLabs +10%) to large (OpenAI ~3.8x, Gladia ~4x, Mistral ~2.3x).

### Cited Findings
- Pipecat benchmark median TTFS (time from end of user speech to final transcript segment): Deepgram nova-3 247 ms; AssemblyAI universal-streaming-english 256 ms; Soniox stt-rt-v6 266 ms; ElevenLabs scribe_v2_realtime 281 ms; AssemblyAI universal-3-5-pro 282 ms; universal-3-6-pro 307 ms; Speechmatics linden-1 369 ms; Google gemini-3.5-transcribe-live 458 ms; Speechmatics (other) 495 ms; OpenAI gpt-4o-transcribe 637 ms; gpt-realtime-whisper 740 ms; Google latest-long 878 ms; Azure 1016 ms; AWS 1136 ms — [Soniox benchmarks page](https://soniox.com/benchmarks)
- Batch vs streaming price per hour — Soniox $0.10 vs $0.12 — [Soniox pricing](https://soniox.com/pricing)
- ElevenLabs $0.20 (Scribe v3) vs $0.22 (Scribe v3 Live) — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
- Deepgram Nova-3 mono $0.26 vs $0.29; multi $0.31 vs $0.35; Flux Multilingual streaming-only $0.47 — [Deepgram pricing](https://deepgram.com/pricing)
- OpenAI gpt-transcribe $0.27 vs gpt-live-transcribe $1.02 — [OpenAI pricing](https://developers.openai.com/api/docs/pricing)
- AssemblyAI ~$0.21 batch vs $0.45 (Universal-3.6 Pro Realtime) or $0.15 (legacy Universal-Streaming, being replaced); streaming is billed per hour of session time — [AssemblyAI pricing](https://www.assemblyai.com/pricing)
- Mistral $0.21 (Mini Transcribe 3) vs $0.48 (Mini Transcribe Realtime 3) (secondary) — [usagepricing.com snapshot](https://www.usagepricing.com/blueprint/activity/mistral-ai-2026-10-22-voxtral-3-audio-pricing)
- Voxtral Realtime: "configurable latency down to sub-200ms"; open weights (Voxtral-Mini-4B-Realtime-2602, Apache 2.0) also available — [Mistral STT docs](https://docs.mistral.ai/capabilities/audio/speech_to_text/)
- Speechmatics Melia 1 $0.24 vs $0.40; Enhanced $0.75 vs $0.80; Linden 1 RT $0.30 — [Speechmatics pricing](https://www.speechmatics.com/pricing)
- Gladia EUR 0.16-0.27 async vs EUR 0.68 real-time — [Gladia pricing](https://www.gladia.io/pricing)
- AWS $0.36 batch vs $0.60 streaming — [AWS Transcribe pricing](https://aws.amazon.com/transcribe/pricing/)
- OpenAI file transcription can also stream output deltas for a completed file (`stream=true` on gpt-transcribe emits `transcript.text.delta` events); this is not live-microphone streaming — [OpenAI speech-to-text guide](https://developers.openai.com/api/docs/guides/speech-to-text)
- Groq's docs list no streaming endpoint, but speed factors of 189-216x real time mean short clips return almost immediately — [Groq speech-to-text docs](https://console.groq.com/docs/speech-to-text)
- Soniox v6 release notes cite "faster voice typing and dictation"; real-time sessions up to 5 hours on a single WebSocket (limit documented for v3, not explicitly re-confirmed for v6) — [Soniox models docs](https://docs.soniox.com/stt/models)
- Artificial Analysis batch speed factors (10-min file): Deepgram Nova-3 564x, Groq Whisper v3 Turbo 400x, MAI-Transcribe-2 342x, AssemblyAI STT-3.7 109x, Gemini 3.5 Transcribe 103x, Scribe v2 86x, Voxtral Mini Transcribe 3 83x, GPT Transcribe 64x, Scribe v3 56x, Soniox v5 Async 48x — [Artificial Analysis STT](https://artificialanalysis.ai/speech-to-text)

### Inferences
- For prose dictation (not a voice agent), sub-second latency is not essential; a "record a paragraph, send it to a fast batch endpoint" loop gets a 60-second clip back in ~1-2 s at 50-500x real time, at batch price and usually batch-level accuracy. Streaming matters mainly if the author wants to watch words appear while speaking.
- Streaming billed by session time (AssemblyAI) penalises long pauses while thinking; per-audio-token or per-audio-second billing with VAD does not.

### Gaps
- No Spanish-language latency measurements; all latency figures are English voice-agent style.
- AssemblyAI-STT-3.7-Realtime, Scribe v3 Live, Voxtral Realtime 3, Flux Multilingual and gpt-live-transcribe were not in the Pipecat latency table captured.
- Partial (interim) result behaviour per vendor was not individually verified in docs.

## 4. Features relevant to an author (punctuation/formatting, custom vocabulary, dictation commands, long files, code-switching)

### Takeaway
Automatic punctuation/capitalisation is universal; custom vocabulary is now strong everywhere (keyterm lists of 100-1,000+ terms, or free-text context prompts), and file limits are generous except at OpenAI (25 MB) and Groq (25-100 MB). No vendor was confirmed to offer Spanish spoken-punctuation / dictation commands, so that layer most likely has to be built in post-processing.

### Cited Findings
- OpenAI gpt-transcribe: `prompt` (context), `keywords` (expected terms; "hints, not required output"), `languages` (expected input languages); upload limit 25 MB per file with guidance to split and avoid mid-sentence cuts; whisper-1 prompt limited to 224 tokens — [OpenAI speech-to-text guide](https://developers.openai.com/api/docs/guides/speech-to-text)
- ElevenLabs Scribe: files up to 5 GB and 15 hours; keyterm prompting up to 1,000 terms (50 chars each) batch, 50 terms realtime, keyterm library up to 10,000 terms on Scribe v3 Live; 90+ languages; word-level timestamps; "no verbatim" mode removing fillers and false starts (Scribe v3/v2 batch, v2 Realtime); experimental "transcript editing"; Scribe v3 accepts secondary language codes for mixed-language audio and Scribe v3 Live has a multilingual mode for mid-sentence switches — [ElevenLabs STT docs](https://elevenlabs.io/docs/overview/capabilities/speech-to-text)
- AssemblyAI: keyterms up to 1,000 (pre-recorded STT-3.7) / 100 (realtime, free); general prompting (beta, +$0.05/h); custom formatting (+$0.03/h) — [AssemblyAI pricing](https://www.assemblyai.com/pricing)
- AssemblyAI code-switching benchmark (vendor-run, 5 language pairs, streaming): STT-3.7-Realtime 6.67%, STT-3.7-Realtime-Agent 7.49%, ElevenLabs Scribe v3 Live 8.32%, Soniox 10.1%, Google 10.2%, Reson8 10.7%, Deepgram 15.4% — [AssemblyAI benchmarks](https://www.assemblyai.com/benchmarks)
- A search summary of AssemblyAI's blog reports a different cut: STT-3.7 6.2% across 16 code-switching datasets vs. Scribe v3 6.8% and Deepgram Nova-3 49.4% (vendor claim, secondary) — [AssemblyAI blog](https://www.assemblyai.com/blog/best-api-models-for-real-time-speech-recognition-and-transcription)
- Deepgram: Smart Formatting included; Keyterm Prompting is a paid add-on ($0.0013/min); Nova-3 multilingual and Flux multilingual cover Spanish+English; the models overview page does not document dictation/spoken punctuation or keyterm limits — [Deepgram pricing](https://deepgram.com/pricing); [Deepgram models & languages](https://developers.deepgram.com/docs/models-languages-overview)
- Mistral Voxtral Mini Transcribe V2: context biasing supported, diarization, up to 3 hours per request, 13 languages — [Mistral STT docs](https://docs.mistral.ai/capabilities/audio/speech_to_text/)
- Soniox: free-text "context" for domain terms/names (improved in v5, v6), mid-sentence language switching and language identification improved in v4-v6, async files up to 5 hours, 60+ languages — [Soniox models docs](https://docs.soniox.com/stt/models)
- Groq Whisper: prompt up to 224 tokens for style/spelling; max file 25 MB free tier / 100 MB dev tier (URL input for larger); segment and word timestamps — [Groq speech-to-text docs](https://console.groq.com/docs/speech-to-text)
- Azure offers Custom Speech training/hosting (custom real-time and batch, endpoint hosting billed per model-hour) — [Azure Speech pricing](https://azure.microsoft.com/en-us/pricing/details/speech/)

### Inferences
- ElevenLabs Scribe v3 has the most author-friendly batch envelope captured (15 h / 5 GB single file, 1,000 keyterms, no-verbatim mode that strips "eh/este" fillers and false starts). Soniox (5 h) and Mistral (3 h) also take whole sessions; OpenAI and Groq require chunking (25 MB is roughly 25-50 min of compressed speech audio).
- "No verbatim"/"transcript editing" modes are double-edged for literary prose: they can silently delete deliberate repetitions or stylistic hesitations. A verbatim transcript plus a separate, reviewable LLM clean-up pass is safer.
- Spoken punctuation ("coma", "punto y aparte", "abrir comillas") is best handled by a deterministic or LLM post-processor, since LLM-based ASR models tend to transcribe the meaning rather than obey commands, and vendor dictation modes historically targeted English.
- Whisper-family 224-token prompts are too small for a novel's full cast list; keyterm APIs with 1,000 terms are not.

### Gaps
- Could not confirm any vendor's Spanish dictation-command support (Deepgram's `dictation` parameter, Azure dictation mode, AWS/Google spoken punctuation); pages fetched did not cover it.
- Deepgram keyterm count limits and whether keyterm prompting works in Spanish on Nova-3/Flux were not confirmed.
- Speechmatics, Gladia, Google, AWS custom-vocabulary specifics and file limits not fetched.
- Spanish-English code-switching specifically (as opposed to the 5-pair aggregate) has no per-vendor numbers.

## 5. Privacy: training defaults, retention, zero-data-retention options

### Takeaway
Defaults differ sharply: OpenAI's transcription endpoint is no-training and no-retention by default; Deepgram (list price) and AssemblyAI reportedly use customer audio for model improvement unless you opt out; Gladia self-serve has training on by default with an opt-out; Speechmatics training is opt-in (for a discount); ElevenLabs retains by default and reserves zero-retention for enterprise. For an unpublished manuscript the opt-outs must be set explicitly, and several vendors' terms could not be verified from primary sources.

### Cited Findings
- OpenAI: `/v1/audio/transcriptions` — not used for training, no abuse-monitoring retention, no application-state retention, Zero Data Retention eligible (via search summary of the official data-controls page). Org-level ZDR is approval-gated, and files uploaded to `/v1/files` persist until deleted — [OpenAI data controls](https://developers.openai.com/api/docs/guides/your-data); [humla.team](https://humla.team/blog/openai-data-retention-policy)
- Deepgram: Model Improvement Program participation is the implied default; opt out per request with `mip_opt_out=true`; when opted out, data is "retained only for as long as needed to process the request"; no retention period is published for non-opted-out audio — [Deepgram MIP docs](https://developers.deepgram.com/docs/the-deepgram-model-improvement-partnership-program)
- Deepgram: a third-party blog states the published pay-as-you-go rates are the ones that enrol you in MIP (i.e. opting out may forfeit the discounted list price) (secondary, unverified against Deepgram's page) — [humla.team on Deepgram](https://humla.team/blog/deepgram-data-retention-policy)
- AssemblyAI: third-party guide says customer audio may be used for training/benchmarking by default; paid customers can opt out by emailing data-opt-out@assemblyai.com; free-tier users cannot opt out (secondary, unverified against AssemblyAI's own policy) — [convertaudiototext.com](https://convertaudiototext.com/blog/opt-out-of-ai-training-with-your-audio)
- ElevenLabs: Zero Retention Mode covers all `/v1/speech-to-text/` endpoints, enabled per request with `enable_logging=false`, but only for "select enterprise customers"; by default data is retained under the Privacy Policy "to enhance services, troubleshoot issues, and ensure the security" of systems; the page does not state whether STT audio trains models — [ElevenLabs Zero Retention Mode](https://elevenlabs.io/docs/resources/zero-retention-mode)
- Gladia: Self-serve — model training enabled by default, opt-out available at any time; Enterprise — training off by default, zero data retention and custom hosting; GDPR, HIPAA, SOC 2 Type II listed — [Gladia pricing](https://www.gladia.io/pricing)
- Speechmatics: model-training programme is opt-in, off by default, and gives 33% off STT rates — [Speechmatics pricing](https://www.speechmatics.com/pricing)
- Mistral offers an open-weights realtime model (Voxtral-Mini-4B-Realtime-2602, Apache 2.0) with edge deployment, i.e. a fully local fallback — [Mistral STT docs](https://docs.mistral.ai/capabilities/audio/speech_to_text/)

### Inferences
- Lowest-friction private options from what was verified: OpenAI gpt-transcribe (no training/retention by default), Deepgram with `mip_opt_out=true` on every request, Speechmatics (do not join the training programme). EU-based Mistral and Gladia (after opt-out) add GDPR jurisdiction.
- "No training" and "no retention" are distinct; an author who wants neither should prefer endpoints that state both, and avoid free tiers where opt-out is unavailable (reported for AssemblyAI).

### Gaps
- No primary-source confirmation obtained for: Soniox, Mistral (La Plateforme), Groq, Google (Chirp/Gemini data-logging terms), Azure, AWS (historically an org-level AI-services opt-out policy), xAI, and AssemblyAI's own policy text. These must be checked directly before choosing.
- Whether Deepgram's `mip_opt_out` changes the price, and ElevenLabs' explicit training stance for Scribe audio on non-enterprise plans, are unconfirmed.
- OpenAI data-controls details came via a search summary rather than a direct fetch of the page.

## 6. Rough total cost to dictate an ~80,000-word novel (30-50 hours of audio)

### Takeaway
Transcription cost is trivial on every option: about $1.20-$15 for 30-50 hours on mainstream batch APIs, at most ~$50 on the priciest streaming/hyperscaler paths, and effectively $0 on several vendors thanks to sign-up credits (Deepgram $200, Speechmatics $100, AssemblyAI $50, Gladia EUR 50).

### Cited Findings
Per-hour rates below are those cited in section 1 (same sources); 30 h and 50 h totals are simple multiplication.

| API / model | Mode | $/h | 30 h | 50 h | Source |
|---|---|---|---|---|---|
| Groq whisper-large-v3-turbo | batch | 0.04 | $1.20 | $2.00 | [Groq](https://console.groq.com/docs/speech-to-text) |
| Groq whisper-large-v3 | batch | 0.111 | $3.33 | $5.55 | [Groq](https://console.groq.com/docs/speech-to-text) |
| Soniox stt-async-v6 | batch | 0.10 | $3.00 | $5.00 | [Soniox](https://soniox.com/pricing) |
| Soniox stt-rt-v6 | streaming | 0.12 | $3.60 | $6.00 | [Soniox](https://soniox.com/pricing) |
| xAI Grok Voice Transcribe 2.0 | batch | 0.10 (secondary) | $3.00 | $5.00 | [AA](https://artificialanalysis.ai/speech-to-text) |
| Microsoft MAI-Transcribe-2 (promo to 2026-12-31) | batch | 0.10 (secondary) | $3.00 | $5.00 | [AA](https://artificialanalysis.ai/speech-to-text) |
| AssemblyAI Universal-2 | batch | 0.15 | $4.50 | $7.50 | [AssemblyAI](https://www.assemblyai.com/pricing) |
| Gladia Solaria-3 | batch | EUR 0.16 | EUR 4.80 | EUR 8.00 | [Gladia](https://www.gladia.io/pricing) |
| OpenAI gpt-4o-mini-transcribe (deprecated) | batch | 0.18 | $5.40 | $9.00 | [OpenAI](https://developers.openai.com/api/docs/pricing) |
| ElevenLabs Scribe v3 | batch | 0.20 (+0.05 keyterms) | $6.00 ($7.50) | $10.00 ($12.50) | [ElevenLabs](https://elevenlabs.io/pricing/api) |
| ElevenLabs Scribe v3 Live | streaming | 0.22 (+0.08 keyterms) | $6.60 ($9.00) | $11.00 ($15.00) | [ElevenLabs](https://elevenlabs.io/pricing/api) |
| AssemblyAI STT-3.7 | batch | 0.21 (+0.05 keyterms) | $6.30 ($7.80) | $10.50 ($13.00) | [AssemblyAI](https://www.assemblyai.com/pricing); [AA](https://artificialanalysis.ai/speech-to-text) |
| Mistral Voxtral Mini Transcribe 3 | batch | 0.21 (secondary) | $6.30 | $10.50 | [snapshot](https://www.usagepricing.com/blueprint/activity/mistral-ai-2026-10-22-voxtral-3-audio-pricing) |
| Mistral Voxtral Small Transcribe 3 | batch | 0.24 (secondary) | $7.20 | $12.00 | [AA](https://artificialanalysis.ai/speech-to-text) |
| Speechmatics Melia 1 | batch / RT | 0.24 / 0.40 | $7.20 / $12.00 | $12.00 / $20.00 | [Speechmatics](https://www.speechmatics.com/pricing) |
| Deepgram Nova-3 mono | batch / RT | 0.258 / 0.288 | $7.74 / $8.64 | $12.90 / $14.40 | [Deepgram](https://deepgram.com/pricing) |
| Deepgram Nova-3 multi | batch / RT | 0.312 / 0.348 | $9.36 / $10.44 | $15.60 / $17.40 | [Deepgram](https://deepgram.com/pricing) |
| OpenAI gpt-transcribe | batch | 0.27 | $8.10 | $13.50 | [OpenAI](https://developers.openai.com/api/docs/pricing) |
| Google Gemini 3.5 Transcribe | batch | 0.30 (secondary) | $9.00 | $15.00 | [AA](https://artificialanalysis.ai/speech-to-text) |
| OpenAI gpt-4o-transcribe / whisper-1 (deprecated) | batch | 0.36 | $10.80 | $18.00 | [OpenAI](https://developers.openai.com/api/docs/pricing) |
| AWS Transcribe | batch / RT | 0.36 / 0.60 | $10.80 / $18.00 | $18.00 / $30.00 | [AWS](https://aws.amazon.com/transcribe/pricing/) |
| Azure Speech 09-2026 | batch | 0.36 (secondary) | $10.80 | $18.00 | [AA](https://artificialanalysis.ai/speech-to-text) |
| AssemblyAI Universal-3.6 Pro Realtime | streaming | 0.45 | $13.50 | $22.50 | [AssemblyAI](https://www.assemblyai.com/pricing) |
| Deepgram Flux Multilingual | streaming | 0.468 | $14.04 | $23.40 | [Deepgram](https://deepgram.com/pricing) |
| Mistral Voxtral Mini Transcribe Realtime 3 | streaming | 0.48 (secondary) | $14.40 | $24.00 | [llmreference](https://www.llmreference.com/model/voxtral-mini-transcribe-realtime-3/mistral-ai-api) |
| Gladia real-time | streaming | EUR 0.68 | EUR 20.40 | EUR 34.00 | [Gladia](https://www.gladia.io/pricing) |
| Speechmatics Enhanced | batch / RT | 0.75 / 0.80 | $22.50 / $24.00 | $37.50 / $40.00 | [Speechmatics](https://www.speechmatics.com/pricing) |
| Google Chirp 3 | batch/stream | 0.96 (secondary) | $28.80 | $48.00 | [AA](https://artificialanalysis.ai/speech-to-text) |
| OpenAI gpt-live-transcribe | streaming | 1.02 | $30.60 | $51.00 | [OpenAI](https://developers.openai.com/api/docs/pricing) |

- Free allowances that cover part or all of the project: Deepgram $200 credit (no expiry); Speechmatics $100; AssemblyAI $50; Gladia EUR 50 (one year); ElevenLabs Starter plan $6/month includes ~30 batch hours; Azure free tier 5 real-time hours/month; AWS 60 min/month for 12 months — [Deepgram](https://deepgram.com/pricing); [Speechmatics](https://www.speechmatics.com/pricing); [AssemblyAI](https://www.assemblyai.com/pricing); [Gladia](https://www.gladia.io/pricing); [ElevenLabs](https://elevenlabs.io/pricing/api); [Azure](https://azure.microsoft.com/en-us/pricing/details/speech/); [AWS](https://aws.amazon.com/transcribe/pricing/)
- Groq bills a 10-second minimum per request, which inflates cost only if dictation is sent as many sub-10-second clips — [Groq speech-to-text docs](https://console.groq.com/docs/speech-to-text)

### Inferences
- Arithmetic check on the brief's premise: 80,000 words / 130 wpm = 615 min = 10.3 h of continuous speech, so 10-15 h raw and 30-50 h with retakes is a sound envelope.
- At these prices the author could transcribe every session on two or three vendors in parallel (e.g. Scribe v3 + Soniox + AssemblyAI, about $25 total for 50 h) and diff the results, which is a cheap way to catch errors and to run a personal Chilean-Spanish bake-off.
- An LLM clean-up pass over ~80,000-250,000 words of raw transcript would likely cost more than the transcription itself, but that is outside this note's scope.
- Costs exclude session-time billing effects for streaming (silence while thinking is billed on AssemblyAI streaming) and any price uplift from privacy opt-outs.

### Gaps
- Azure real-time, Google Gemini live, and AssemblyAI-STT-3.7-Realtime hourly rates are not confirmed from vendor pages, so their rows are omitted or marked secondary.
- Taxes/VAT and minimum top-up amounts per vendor were not checked.
