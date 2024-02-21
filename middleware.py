class Middleware:
	def __init__(self, config=None):
		self.config = config


	def handle_request(self, request):
		return request


	def handle_response(self, response):
		return response