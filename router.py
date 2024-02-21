import re
from .errors import HttpErrorResponse


class Route:
    def __init__(self, **kwargs):
        self.children = {}
        self.is_terminal = False
        self.value = None
        self.handlers = {}
        self.alias = kwargs.get('alias', None)

    
    def insert(self, route, method, func):
        node = self
        tokens = [i for i in route.split('/') if i]

        for token in tokens:     
            match = re.match(r'\{([^}]+)\}', token)
            if match:
                token = '*' 

            if not node.children.get(token, False):
                node.children[token] = Route()

                if token == "*":
                    node.children[token].alias = match.group(1)
                
            node = node.children[token]
        
        node.is_terminal = True
        node.handlers[method] = func
        
        
    def find(self, route, method, **kwargs):
        node = self
        tokens = [i for i in route.split('/') if i]
        
        for token in tokens:
            if node.children.get(token, None) == None:
                if '*' in node.children:
                    node = node.children["*"]
                    params = kwargs.get('params', {})
                    params[node.alias] = token

                    continue

                else:
                    return None
                
            node = node.children[token] 
        func = node.handlers.get(method, None)
        
        if not node.is_terminal:
            raise HttpErrorResponse(status=404, detail={'message': 'bad request'})

        if func is None:
            raise HttpErrorResponse(status=405, detail={'message': 'not allowed'})
            
        return func
