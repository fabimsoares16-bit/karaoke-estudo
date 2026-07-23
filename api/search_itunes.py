# Função serverless da Vercel: /api/search_itunes?term=...
# Proxy para a busca do iTunes (contorna bloqueio de CORS em navegadores móveis).
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.urlparse(self.path).query
        term = urllib.parse.parse_qs(qs).get('term', [''])[0]
        url = (
            "https://itunes.apple.com/search?term="
            + urllib.parse.quote(term)
            + "&entity=song&media=music&limit=18"
        )
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'KaraokeEstudo/1.0'},
            )
            data = urllib.request.urlopen(req, timeout=9).read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            body = json.dumps({'error': str(e)}).encode('utf-8')
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
