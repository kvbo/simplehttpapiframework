from .router import Route
from .errors import HttpErrorResponse
from .middleware import Middleware

from http.server import BaseHTTPRequestHandler
from typing import Any
import json
from http.cookies import BaseCookie
from urllib.parse import urlparse
from datetime import datetime

class RouteInsertMixin:
    def GET(self, route):
        def wrapper(fn):
            def inner(*args, **kwargs):
                self.routes.insert(route, 'GET', fn)        
            inner()
        return wrapper
    
    def POST(self, route):
        def wrapper(fn):
            def inner(*args, **kwargs):
                self.routes.insert(route, 'POST', fn)
                
            inner()
        return wrapper    


    def PUT(self, route):
        def wrapper(fn):
            def inner(*args, **kwargs):
                self.routes.insert(route, 'PUT', fn)
                
            inner()
        return wrapper  
    

    def PATCH(self, route):
        def wrapper(fn):
            def inner(*args, **kwargs):
                self.routes.insert(route, 'PATCH', fn)
                
            inner()
        return wrapper  


    def DELETE(self, route):
        def wrapper(fn):
            def inner(*args, **kwargs):
                self.routes.insert(route, 'DELETE', fn)
                
            inner()
        return wrapper      
    


class API(RouteInsertMixin):
    _instance = None

    def __new__(cls, *arg, **kwargs):
        if cls._instance is None:
            cls._instance = super(API, cls).__new__(cls)
        return cls._instance


    def __init__(self, *arg, **kwargs):
        if kwargs.get('request', False):
            super().__init__(*arg, **kwargs)

        self.routes = Route()
        self.middlewares = []


    def use(self, middleware: Middleware, config=None) -> None:

        obj = (middleware, config)
        self.middlewares.append(obj)


    def handler(self, request_handler: BaseHTTPRequestHandler):
        req = Request(request_handler)

        try:
            fn = self.routes.find(req.path, req.method, params=req.params)

            initiated_middleware = []
            for middleware in self.middlewares:
                m = middleware[0](config=middleware[1])
                temp = initiated_middleware.copy()

                initiated_middleware = [m]
                initiated_middleware.extend(temp)

                req = m.handle_request(req)


            if fn is not None:
                res = fn(req)
                if res:
                    for middleware in initiated_middleware:
                        res = middleware.handle_response(res)

                    res.respond(request_handler)
                    
                else:
                    raise HttpErrorResponse(status=500, detail={})
            else:
                raise HttpErrorResponse(status=404, detail={'message': 'Bad request'})
            

        except HttpErrorResponse as e:
            e.respond(request_handler)



class Request:
    def __init__(self, request_handler) -> None:

        self.headers = request_handler.headers
        raw = request_handler.rfile.read(int(self.headers.get('Content-Length', 0)))

        self._parse(request_handler.path)

        self.method = request_handler.command
        self.params = params={}

        self.raw = raw
        content_length = self.headers.get('Content-Length', 0)
        content_type = self.headers.get('Content-Type', 'text/plain')

        self.data = self._transform(self.raw, content_type, content_length)

    
    def _transform(self, raw, content_type, content_length=0):
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