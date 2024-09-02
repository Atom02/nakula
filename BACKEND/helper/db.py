
import os
import mariadb
from dotenv import load_dotenv, find_dotenv

class MyDb:
	open = False
	db = None
	cursor = None
	cur = None

	def __init__(self,dbIdentifier='DB'):
		# print(dir(mariadb))
		if(self.open == False):
			self.open = False
			self.db = None
			self.cursor = None
			self.cur = self.cursor
			self.__openDb(dbIdentifier=dbIdentifier)

	def __openDb(self,dbIdentifier = 'DB'):
		self.open = False
		self.db = None
		self.cursor = None
		self.cur = self.cursor
		env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'env')
		# print(env_file_path)
		load_dotenv(env_file_path)
		# print(os.getenv("DBHOST"))
		conv = {
			mariadb.FIELD_TYPE.DATE: str,
			mariadb.FIELD_TYPE.DATETIME: str,
			mariadb.FIELD_TYPE.TIME:str,
			mariadb.FIELD_TYPE.TIMESTAMP:str
		}
		self.db = mariadb.connect(			
			user=os.getenv(dbIdentifier+"_USERNAME"),
			password=os.getenv(dbIdentifier+"_PASSWORD"),
			host=os.getenv(dbIdentifier+"_HOST"),
			port=int(os.getenv(dbIdentifier+"_PORT")),
			database=os.getenv(dbIdentifier+"_NAME"),
			converter = conv
		)

		self.db.auto_reconect = True
		# print(dir(self.db))
		# self.open = True
		self.cursor = self.db.cursor(dictionary = True)
		self.cur = self.cursor
	
	def is_connected(connection):
		try:
			self.db.ping()
		except:
			return False
		return True

	def get(self):
		# if self.open == False:
		# 	self.__openDb()
		if self.is_connected() == False:
			self.__openDb()
		# self.cursor = self.db.cursor(dictionary = True)
		# self.cur = self.cursor
		return self.cur
	
	def getDb(self):
		return self.get()

	def close(self):		
		if(self.db is not None):
			self.db.cursor().close()
			self.db.close()			
			self.db = None
			self.open = False
			self.cursor = None
			self.cur = self.cursor
	
	def commit(self):
		self.db.commit()
		
	def rollback(self):
		self.db.rollback()

	

