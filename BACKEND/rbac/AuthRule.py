from .Auth import Auth

class AuthRule(Auth):
	name = None
	type = None
	description = None
	group = None
	rule = None
	data = None
	created = None
	updated = None
	rule_name = None

	def execute(self, item = None, params = {}, **kwargs):
		pass
	