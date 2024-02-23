from .requests import Request
from .responses import Response


class Middleware:
	def __init__(self, config=None):
		self.config = config


	def handle_request(self, request: Request):
		return request


	def handle_response(self, response: Response):
		return response