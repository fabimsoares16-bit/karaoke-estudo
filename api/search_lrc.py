# Função serverless da Vercel: /api/search_lrc?q=...
# Proxy para a busca de letras sincronizadas do lrclib (contorna o CORS).
from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = urllib.parse.urlparse(self.path).query
        query = urllib.parse.parse_qs(qs).get('q', [''])[0]
        url = "https://lrclib.net/api/search?q=" + urllib.parse.quote(query)
        try:
            req = urllib.request.Request(
                url, headers={'User-Agent': 'KaraokeEstudo/1.0 (https://github.com/fabio/karaoke)'})
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
