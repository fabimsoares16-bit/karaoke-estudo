# Função serverless da Vercel: /api/lyrics_fallback?q=...
# Reserva para quando o lrclib está fora: busca letra simples (sem sincronia)
# no lyrics.ovh, testando combinações de artista/título automaticamente.
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json


def _candidates(query):
    words = query.split()
    pairs = []
    if len(words) < 2:
        return pairs
    for i in range(1, len(words)):
        a = ' '.join(words[:i])
        b = ' '.join(words[i:])
        pairs.append((a, b))  # primeiro = artista
        pairs.append((b, a))  # invertido = título
    seen, out = set(), []
    for p in pairs:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out[:6]  # limita tentativas para caber no tempo da função


def _lyrics_ovh(query):
    for artist, title in _candidates(query):
        url = ('https://api.lyrics.ovh/v1/'
               + urllib.parse.quote(artist) + '/' + urllib.parse.quote(title))
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            parsed = json.loads(urllib.request.urlopen(req, timeout=4).read())
            lyrics = (parsed.get('lyrics') or '').strip()
            if not lyrics:
                continue
            lines = [l for l in lyrics.splitlines() if l.strip()]
            return {
                'id': abs(hash(artist + '|' + title)) % 1000000000,
                'trackName': title.title(),
                'artistName': artist.title(),
                'albumName': '',
                'duration': max(round(len(lines) * 3.2), 60),
                'syncedLyrics': None,
                'plainLyrics': lyrics,
            }
        except Exception:
            continue
    return None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.urlparse(self.path).query
        query = urllib.parse.parse_qs(qs).get('q', [''])[0]
        try:
            item = _lyrics_ovh(query)
            self._json([item] if item else [])
        except Exception as e:
            self._json({'error': str(e)}, status=502)

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)
