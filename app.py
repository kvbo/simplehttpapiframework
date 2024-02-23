from .router import Route
from .errors import HttpErrorResponse
from .middleware import Middleware
from .responses import Response
from .requests import Request


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



