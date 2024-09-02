from .Auth import Auth
class AuthGroup(Auth):
	name = None
	desc = None
	created = None
	updated = None
	def __init__(self,name = None):
		self.name = name