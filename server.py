import http.server
import socketserver
import urllib.request
import urllib.parse
import urllib.error
import re
import json

PORT = 8000
FETCH_TIMEOUT = 10  # segundos por tentativa
RETRIES = 1


def fetch(url, headers, retries=RETRIES):
    """Baixa uma URL com timeout e algumas tentativas (lrclib/youtube podem
    responder 502 ou travar intermitentemente)."""
    last_err = None
    for _ in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            return urllib.request.urlopen(req, timeout=FETCH_TIMEOUT).read()
        except Exception as e:
            last_err = e
    raise last_err


def _ovh_candidates(query):
    """Gera pares (artista, titulo) plausiveis a partir da busca livre.
    Testa os dois sentidos porque nao sabemos qual palavra e o artista."""
    words = query.split()
    pairs = []
    if len(words) < 2:
        return pairs
    for i in range(1, len(words)):
        a = ' '.join(words[:i])
        b = ' '.join(words[i:])
        pairs.append((a, b))  # primeiro = artista
        pairs.append((b, a))  # invertido = titulo
    seen, out = set(), []
    for p in pairs:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out[:8]  # limita tentativas para nao demorar


def lyrics_ovh(query):
    """Fallback quando o lrclib esta fora: busca letra simples no lyrics.ovh
    e devolve um item no mesmo formato do lrclib (sem sincronia)."""
    for artist, title in _ovh_candidates(query):
        url = ('https://api.lyrics.ovh/v1/'
               + urllib.parse.quote(artist) + '/' + urllib.parse.quote(title))
        try:
            data = fetch(url, {'User-Agent': 'Mozilla/5.0'}, retries=0)
            parsed = json.loads(data)
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


class KaraServer(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Evita que o navegador sirva um index.html/JS antigo em cache.
        self.send_header('Cache-Control', 'no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith('/api/search_yt?q='):
            query = urllib.parse.unquote(self.path.split('q=')[1])
            url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
            try:
                html = fetch(url, {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}).decode('utf-8')
                match = re.search(r'"videoId":"([^"]{11})"', html)
                video_id = match.group(1) if match else None
                self._send_json({'videoId': video_id})
            except Exception as e:
                self._send_json({'videoId': None, 'error': str(e)}, status=502)
            return

        if self.path.startswith('/api/search_lrc?q='):
            query = urllib.parse.unquote(self.path.split('q=')[1])
            url = "https://lrclib.net/api/search?q=" + urllib.parse.quote(query)
            try:
                data = fetch(url, {'User-Agent': 'KaraokeEstudo/1.0 (https://github.com/fabio/karaoke)'})
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(data)
            except Exception as e:
                self._send_json({'error': str(e)}, status=502)
            return

        if self.path.startswith('/api/lyrics_fallback?q='):
            query = urllib.parse.unquote(self.path.split('q=', 1)[1])
            try:
                item = lyrics_ovh(query)
                self._send_json([item] if item else [])
            except Exception as e:
                self._send_json({'error': str(e)}, status=502)
            return

        # Serve arquivos normais (index.html, etc)
        return super().do_GET()


class ThreadingServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


with ThreadingServer(("", PORT), KaraServer) as httpd:
    print(f"Servidor Karaokê rodando em http://localhost:{PORT}")
    print("O app agora busca o áudio automaticamente no YouTube!")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
