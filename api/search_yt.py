# Função serverless da Vercel: /api/search_yt?q=...
# Descobre o ID do primeiro vídeo do YouTube para a busca informada.
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import re
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.urlparse(self.path).query
        query = urllib.parse.parse_qs(qs).get('q', [''])[0]
        try:
            url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(query)
            req = urllib.request.Request(
                url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            html = urllib.request.urlopen(req, timeout=9).read().decode('utf-8')
            match = re.search(r'"videoId":"([^"]{11})"', html)
            video_id = match.group(1) if match else None
            self._json({'videoId': video_id})
        except Exception as e:
            self._json({'videoId': None, 'error': str(e)}, status=502)

    def _json(self, obj, status=200):
        body = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)
