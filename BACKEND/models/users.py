class User:
    db = None
    def __init__(self, db=None):
        if db == None:
			raise ValueError("Where IS THE DB??")
        self.db = db