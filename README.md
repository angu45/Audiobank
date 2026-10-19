# Audiobook Studio (lean core)

Static, no-build app: HTML + CSS + ES modules + PyScript. Deploy to Vercel as-is (no `vercel.json` needed). Run locally with `python3 -m http.server` and open http://localhost:8000 (the service worker and fetch need http, not file://).

## What works
- Script editor, TXT/MD/JSON import (button or drag-and-drop), autosave to IndexedDB, project list, restore last project.
- **PyScript** (`python/script_analyzer.py`): chapter detection, sentence-safe chunking (paragraph, then sentence, then whitespace), stats, reading-time and size estimates, warnings for URLs, symbols, duplicate/empty chapters, long paragraphs.
- Playback of chunks through the **Web Speech API** with real browser voices, speed/pitch/volume, pauses, presets, pronunciation dictionary (applied only when speaking), play/pause/stop/prev/next, keyboard shortcuts.
- Dark/light theme, offline app shell via service worker, mobile layout.
- Export project JSON and script TXT.

## Limits (honest)
- Web Speech audio cannot be captured, so **no WAV/MP3 export** and no audio processing yet. Real export needs a synthesizer that returns audio (Piper/ONNX in browser, or an optional server). `config/models.json` lists Piper as "optional backend, not implemented".
- Voices depend on the device. Cloud voices do not work offline.
- PyScript needs the CDN on first load (cached afterward by the service worker).
- Untested in a browser in this build: only syntax checks were run.

## Not built yet
Chapter reorder/split/merge, per-chapter voices, generation queue with retry, history, audio tools, metadata editor, voice library, tests doc. The `S.chunks` structure and the provider split (`run()` in `app.js`) are the place to add them.

## Dependencies
PyScript 2024.11.1 (Apache-2.0, CDN). Nothing else.
