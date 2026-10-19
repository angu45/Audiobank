"""Runs in the browser via PyScript/Pyodide. Detects chapters, splits text into
TTS-safe chunks (paragraph > sentence > whitespace), and reports stats/warnings."""
import json, re
from pyscript import window
from pyodide.ffi import create_proxy

HEAD = re.compile(r'^\s*(chapter\s+\w+.*|part\s+[ivxlc\d]+.*|introduction|preface|prologue|epilogue|conclusion)\s*$', re.I)
SENT = re.compile(r'(?<=[.!?।。])\s+')
URL = re.compile(r'https?://\S+')
WPM = 150

def hard_split(s, limit):
    out = []
    while len(s) > limit:
        cut = s.rfind(' ', 0, limit)
        cut = cut if cut > 0 else limit
        out.append(s[:cut].strip())
        s = s[cut:].strip()
    if s:
        out.append(s)
    return out

def units(paragraph, limit):
    if len(paragraph) <= limit:
        return [paragraph]
    res = []
    for sent in SENT.split(paragraph):
        res.extend([sent] if len(sent) <= limit else hard_split(sent, limit))
    return res

def pack(paragraphs, limit):
    chunks, cur = [], ''
    for p in paragraphs:
        for u in units(p, limit):
            if cur and len(cur) + len(u) + 1 > limit:
                chunks.append(cur)
                cur = u
            else:
                cur = f'{cur}\n{u}' if cur else u
    if cur:
        chunks.append(cur)
    return chunks

def analyze(text, limit):
    limit = int(limit)
    chapters, title, buf, seen, warnings = [], 'Opening', [], set(), []

    def close():
        paras = [p.strip() for p in '\n'.join(buf).split('\n\n') if p.strip()]
        if paras or title != 'Opening':
            chapters.append({'title': title, 'paragraphs': paras})

    for line in text.split('\n'):
        if HEAD.match(line):
            close()
            title, buf = line.strip(), []
            if title.lower() in seen:
                warnings.append(f'Duplicate heading: {title}')
            seen.add(title.lower())
        else:
            buf.append(line)
    close()

    for c in chapters:
        if not c['paragraphs']:
            warnings.append(f'Empty chapter: {c["title"]}')
        for p in c['paragraphs']:
            if len(p) > 1500:
                warnings.append(f'Very long paragraph in "{c["title"]}" ({len(p)} characters); it will be split by sentence.')
        c['chunks'] = pack(c.pop('paragraphs'), limit)

    words = len(text.split())
    minutes = round(words / WPM, 1)
    if URL.search(text):
        warnings.append(f'{len(URL.findall(text))} URL(s) found; consider a pronunciation rule.')
    if re.search(r'[#*_~`<>{}\[\]|^]{2,}', text):
        warnings.append('Unusual symbols found (e.g. Markdown markup); they may be read aloud.')
    stats = {
        'characters': len(text), 'words': words,
        'sentences': len([s for s in SENT.split(text) if s.strip()]),
        'paragraphs': len([p for p in text.split('\n\n') if p.strip()]),
        'chapters': len(chapters), 'estimated_minutes': minutes,
        'estimated_audio_mb': round(minutes * 60 * 8000 / 1e6, 1),  # 64 kbps MP3
    }
    return json.dumps({'stats': stats, 'chapters': chapters, 'warnings': warnings[:20]})

window.analyzeScript = create_proxy(analyze)
window.dispatchEvent(window.Event.new('pyready'))
