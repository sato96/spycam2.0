import mysql.connector
from mysql.connector import Error

class MysqlConnector(object):
	"""docstring for ClassName"""
	def __init__(self, host, database, username, password, logger):
		self._host = host
		self._database = database
		self._username = username
		self._password = password
		self._connection = None
		self._logger = logger

	def _connect(self):
		self._connection = mysql.connector.connect(host=self._host,
											 database=self._database,
											 user=self._username,
											 password=self._password)
	def query(self, text):
		result = None
		r = None
		try:
			self._connect()
			if self._connection.is_connected():
				db_Info = self._connection.get_server_info()
				cursor = self._connection.cursor()
				cursor.execute(text)
				record = cursor.fetchall()
				result = record
				r = []
				for row in result:
					j = {}
					for col in range(len(cursor.column_names)):
						j[cursor.column_names[col]] = row[col]
					r.append(j)

		except Error as e:
			self._logger.error(e)
		finally:
			if self._connection.is_connected():
				cursor.close()
				self._connection.close()
		return r

	def update(self,text):
		result = None
		try:
			self._connect()
			if self._connection.is_connected():
				db_Info = self._connection.get_server_info()
				cursor = self._connection.cursor()
				cursor.execute(text)
				self._connection.commit()
				record = cursor.fetchall()
				result = record

		except Error as e:
			self._logger.error(e)
		finally:
			if self._connection.is_connected():
				cursor.close()
				self._connection.close()
		return result

	def update(self,text):
		result = None
		try:
			self._connect()
			if self._connection.is_connected():
				db_Info = self._connection.get_server_info()
				cursor = self._connection.cursor()
				cursor.execute(text)
				self._connection.commit()
				record = cursor.fetchall()
				result = record

		except Error as e:
			self._logger.error(e)
		finally:
			if self._connection.is_connected():
				cursor.close()
				self._connection.close()
		return result
