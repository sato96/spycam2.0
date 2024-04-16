from werkzeug.security import generate_password_hash, check_password_hash


class AppLogin:

	@staticmethod
	def createBearer(usrId, connector):
		bearer = generate_password_hash(usrId)
		upd = "UPDATE usr_users SET token = '" + bearer + "' WHERE chat_id = '" + usrId + "'"
		up = connector.update(upd)
		try:
			if up is not None:
				upd = "UPDATE usr_users SET expiration_date = date_add(SYSDATE(),interval 5 minute) WHERE chat_id = " + usrId
				up = connector.update(upd)
			else:
				bearer = 'ko'
		except:
			bearer = 'ko'
		return bearer

	@staticmethod
	def checkBearer(bearer, ws, connector):
		try:
			txt = "SELECT COUNT(*) as count FROM usr_users uu WHERE uu.expiration_date > SYSDATE() and uu.token = '" + bearer +"' and uu.role in (select rm.id_role from rol_microservices rm join ws_microservices wm on rm.id_microservice = wm.id where wm.code = '" + ws +"')"
			res = connector.query(txt)
			if res[0]['count'] != 0 and type(res[0]['count']) == int:
				resp = 'ok'
				code = 200
			elif res is None:
				code = 500
			else:
				resp = 'ko'
				code = 401
		except:
			code = 500
		return code
