import socketserver
from typing import *
from .app import API
import http.server

 
class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self._internal()

    def do_POST(self) -> None:
        self._internal()

    def do_DELETE(self) -> None:
        self._internal()

    def do_PUT(self) -> None:
        self._internal()

    def _internal(self):
        self.server.app.handler(self)
        

class Server(socketserver.TCPServer):
    def __init__(self, app: API, *args, **kwargs, ) -> None:

        super().__init__(*args, **kwargs, bind_and_activate=True, )
        self.app = app


def run(app, host="", port=9000):
    with Server(server_address=(host, port), app=app, RequestHandlerClass=RequestHandler) as httpd:
        print("serving at port", port)
        httpd.serve_forever()        
