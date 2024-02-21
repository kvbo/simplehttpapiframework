from http.server import BaseHTTPRequestHandler
import json


class HttpErrorResponse(BaseException):
    def __init__(self, status=404, detail={}) -> None:
        self.status = status
        self.detail = detail


    def respond(self, request_handler: BaseHTTPRequestHandler):
        request_handler.send_response(self.status)
        request_handler.send_header('Content-Type', 'application/json')
        request_handler.end_headers()

        request_handler.wfile.write(json.dumps(self.detail).encode('utf-8'))