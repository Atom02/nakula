from .Auth import Auth
class AuthRole(Auth):
	name = None
	created = None
	updated = None
	description = None
	group = None
	rule = None
	data = None

	def __init__(self, name = None):
		self.name = name