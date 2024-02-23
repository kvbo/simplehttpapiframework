from http.server import BaseHTTPRequestHandler
from typing import Any
import json
from http.cookies import BaseCookie
from datetime import datetime



class Response:
    def __init__(self, data=None, status=200):
        self._status = status
        self._cookies = BaseCookie()
        self._headers = {}
        self.data: Any | None = data


    def set_header(self, key, value):
        self._headers[key] = value
        

    def set_cookie(self, 
        name, 
        value, 
        expires: datetime | None = None ,
        path=None,
        comment=None,
        domain=None,
        max_age=None,
        secure=None,
        version="",
        httponly=False,
        samesite=None                            
    ) -> None:

        self._cookies[name] = value

        if expires is not None:
            expires_str = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
            self._cookies[name]['Expires'] = expires_str


        if path:
            self._cookies[name]['Path'] = path        
        if domain:
            self._cookies[name]['Comment'] = comment
        if domain:
            self._cookies[name]['Domain'] = domain
        if max_age is not None:
            self._cookies[name]['Max-Age'] = max_age
        if secure is not None:
            self._cookies[name]['Secure'] = secure
        if version:
            self._cookies[name]['Version'] = version

        self._cookies[name]['HttpOnly'] = httponly
        if samesite:
            self._cookies[name]['SameSite'] = samesite


    
    @property
    def cookies(self):
        return self._cookies
    

    @property
    def headers(self):
        return self._headers
            

    def send_headers(self, request_handler):
        request_handler.send_response(200)

        for key, value in self._headers.items():
            request_handler.send_header(key, value)


        sep= "\r\n"
        cookies = self._cookies.output(header="", sep=sep).split(sep)
        

        for cookie in cookies:
            request_handler.send_header('Set-Cookie', cookie)
        
        request_handler.end_headers()


    def respond(self, request_handler: BaseHTTPRequestHandler):
        self.send_headers(request_handler)
        request_handler.wfile.write(bytes(self.data, 'utf-8'))