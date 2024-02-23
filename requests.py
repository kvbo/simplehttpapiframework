from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import urlparse


class Request:
    def __init__(self, request_handler) -> None:
        self._parse(request_handler.path)
        self._headers = request_handler.headers

        self.raw = request_handler.rfile.read(int(self._headers.get('Content-Length', 0)))
        self.method = request_handler.command
        self.params = params={}

        content_length = self._headers.get('Content-Length', 0)
        content_type = self._headers.get('Content-Type', 'text/plain')

        self.data = self._negotiate(self.raw, content_type, content_length)
        self._cookies = self._cookify()


    def _cookify(self):
        cookies = {}

        for pair in [x for x in self._headers.get('Cookie', '').split(';') if x]:
            key, value = pair.split('=')

            cookies[key] = value
        return cookies


    @property
    def cookies(self):
        return self._cookies


    @property
    def headers(self):
        return self._headers

    
    def _negotiate(self, raw, content_type, content_length=0):
        match content_type:
            case 'application/json':
                data = json.loads(raw)
            
            case _ :
                data = str(raw)
        return data
    

    def _parse(self, path):   
        _ = urlparse(path)
        self.path = _.path
        self.query = _.query

        return (self.path, self.query)

