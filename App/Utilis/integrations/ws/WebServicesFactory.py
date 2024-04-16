from Utilis.integrations.auth.Login import AppLogin
from Utilis.integrations.response.ResponseFactory import ResponseFactory
from flask import request
import json
import traceback

class WebServiceFactory:

	@staticmethod
	def wsHandler(ws, request, connector,logger, func):
		code = 500
		try:
			headers = request.headers
			bearer = headers.get('Authorization')
			if bearer is not None:
				token = bearer.split()[1]
				auth = AppLogin.checkBearer(token, ws, connector)
			else:
				auth = 401
			if auth == 200:
				args = request.args
				serv = args.get('serv')
				if serv == None:
					r = func(ws, request, connector, logger)
				else:
					r = func(ws, request, connector, logger, serv)
			else:
				responses = ResponseFactory.generateAnswer(ws, 401, connector)
				status = 'ko'
				code = 401
				r = ResponseFactory.makeResponse(status, responses, code) 
		except Exception as e:
			status = 'ko'
			code = 500
			responses = ResponseFactory.generateAnswer(ws, 500, connector)
			logger.exception(traceback.format_exc())
			r = ResponseFactory.makeResponse(status, responses, code) 
		return r

	@staticmethod
	def login(ws, request, connector,logger):
		bearer = ''
		try:
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			bearer = AppLogin.createBearer(dati['chat_id'], connector)
			resp = ''
			if bearer == 'ko':
				code = 401
				resp = ''
				status = 'ko'
			else:
				code = 200
				status = 'ok'
		except Exception as e:
			status = 'ko'
			logger.error(e)
			code = 500
		resp = ResponseFactory.generateAnswer(ws, code, connector)
		r = ResponseFactory.makeResponse(status, resp, code, {'token': bearer})
		return r


	@staticmethod
	def signIn(ws, request, connector,logger):
		body = request.data
		dati = json.loads(body.decode('utf-8'))	
		try:	
			#tre query:
			#Se esiste l'utente, se il servizio è censito e se il numero di utenti massimo è stato raggiunto
			qry1 = "SELECT count(*) count from usr_users WHERE username = '" + dati["user"]["username"] + " 'AND chat_id = '" + dati["user"]["chat_id"] + "' AND id_service = (SELECT id from ser_services where code = '" + dati["service"] +"')"
			cond1 = connector.query(qry1)[0]['count']
			qry2 = "SELECT count(*) count from ser_services where code = '" + dati["service"] + "'"
			cond2 = connector.query(qry2)[0]['count']
			qry3 = "SELECT count(*) count from par_parameters pp where pp.code = 'MAX_USERS' and CAST(pp.value AS INTEGER) > (SELECT count(*) from usr_users uu )"
			cond3 = connector.query(qry3)[0]['count']
			if cond1 == 0 and cond2 != 0 and cond3 != 0:	
				#check se il servizio è censito e se il numero massimo di utenti è raggiunto
				txt = "INSERT INTO usr_users(username, chat_id, id_service,insert_date) Values ('" + dati["user"]["username"] + "', '" + dati["user"]["chat_id"] + "', " + "(SELECT id from ser_services where code = '" + dati["service"] + "'), SYSDATE())"
				out = connector.insert(txt)
				#da fixare qua
				status = 'ok'
				code = 200
			else:
				status = 'ko'
				code = 401
		except Exception as e:
			status = 'ko'
			code = 500
			logger.error(e)
			code = 500
		resp = ResponseFactory.generateAnswer(ws, code, connector)
		r = ResponseFactory.makeResponse(status, resp, code)
		return r
