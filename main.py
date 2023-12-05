from flask import Flask, make_response, request
from flask_cors import cross_origin
import requests
import mysql.connector
from mysql.connector import Error
import json
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import logging


##todo -> uniformare i response gli errori per tutti i ws disponibili, bisogna iniziare a essere formale 17/10/2023 - Fatto
##gestire in oggetti diversi la connessione al db e gli utenti (anche se è da vedere)
##17/10/2023 - fare classi intere per gestire le cose (esempio una classe che gestisca il servizio, una per il db etc)


def shutdown_server():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()

def query(text):
	result = None
	try:
		connection = mysql.connector.connect(host='localhost',
											 database='spyCam',
											 user='SPY_CAM',
											 password='spycam')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			cursor = connection.cursor()
			cursor.execute(text)
			record = cursor.fetchall()
			result = record

	except Error as e:
		print("Error while connecting to MySQL", e)
	finally:
		if connection.is_connected():
			cursor.close()
			connection.close()
	return result
def update(text):
	result = None
	try:
		connection = mysql.connector.connect(host='localhost',
											 database='spyCam',
											 user='SPY_CAM',
											 password='spycam')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			cursor = connection.cursor()
			cursor.execute(text)
			connection.commit()
			record = cursor.fetchall()
			result = record

	except Error as e:
		print("Error while connecting to MySQL", e)
	finally:
		if connection.is_connected():
			cursor.close()
			connection.close()
	return result

def insert(text):
	result = None
	try:
		connection = mysql.connector.connect(host='localhost',
											 database='spyCam',
											 user='SPY_CAM',
											 password='spycam')
		if connection.is_connected():
			db_Info = connection.get_server_info()
			cursor = connection.cursor()
			cursor.execute(text)
			connection.commit()
			record = cursor.fetchall()
			result = record

	except Error as e:
		print("Error while connecting to MySQL", e)
	finally:
		if connection.is_connected():
			cursor.close()
			connection.close()
	return result

def createBearer(usrId):
	bearer = generate_password_hash(usrId)
	upd = "UPDATE usr_users SET token = '" + bearer + "' WHERE chat_id = '" + usrId + "'"
	up = update(upd)
	try:
		if up is not None:
			upd = "UPDATE usr_users SET expiration_date = date_add(SYSDATE(),interval 5 minute) WHERE chat_id = " + usrId
			up = update(upd)
		else:
			bearer = 'ko'
	except:
		bearer = 'ko'
	return bearer

def checkBearer(bearer, ws):
	try:
		txt = "SELECT COUNT(*) FROM usr_users uu WHERE uu.expiration_date > SYSDATE() and uu.token = '" + bearer +"' and uu.role in (select rm.id_role from rol_microservices rm join ws_microservices wm on rm.id_microservice = wm.id where wm.code = '" + ws +"')"
		res = query(txt)
		if res[0][0] != 0 and type(res[0][0]) == int:
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

def generateAnswer(ws, httpCode, service = None):
	ws = str(ws)
	httpCode = str(httpCode)
	if service == None:
		qry = "Select CASE WHEN count(*) > 0 then wr.`text` ELSE 	(SELECT wr2.text from ws_microservices wm2 JOIn ws_responses wr2 on wm2.id = wr2.id_microservice WHERE wm2.id_service is NULL and wm2.code = '"+ ws + "' and wr2.error_code is null) END as `text`from ws_microservices wm JOIn ws_responses wr on wm.id = wr.id_microservice WHERE wm.id_service is null and wm.code = '" + ws + "' and wr.error_code = " + httpCode
	else:
		service = str(service)
		qry = "Select CASE WHEN count(*) > 0 then wr.`text` ELSE 	(SELECT wr2.text from ws_microservices wm2 JOIn ws_responses wr2 on wm2.id = wr2.id_microservice WHERE wm2.id_service = "+ service + " and wm2.code = '"+ ws + "' and wr2.error_code is null) END as `text`from ws_microservices wm JOIn ws_responses wr on wm.id = wr.id_microservice WHERE wm.id_service = " + service +" and wm.code = '" + ws + "' and wr.error_code = " + httpCode
	ans = query(qry)
	return str(ans[0][0])

def makeResponse(status, response, code):
	resp = {"status": status, "response": response}
	myResponse = make_response(json.dumps(resp))
	myResponse.status_code = code
	return myResponse


logging.basicConfig(filename='tmp/mainApp.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)
app = Flask('Main')


#ws di login per il bearer e ws di controllo del bearer. Mettere il bearer con una scadenza
@app.route('/login', methods = ['POST'])
def Login():
	body = request.data
	dati = json.loads(body.decode('utf-8'))
	bearer = createBearer(dati['chat_id'])
	resp = ''
	if bearer == 'ko':
		code = 401
		resp = 'Non autorizzato'
	else:
		code = 200
	r = {"token": bearer, 'response': resp}
	myResponse = make_response(json.dumps(r))
	myResponse.status_code = code
	return myResponse

@app.route('/registrati', methods = ['POST'])
def SignIn():
	body = request.data
	dati = json.loads(body.decode('utf-8'))	
	ws = '/registrati'
	try:	
		#tre query:
		#Se esiste l'utente, se il servizio è censito e se il numero di utenti massimo è stato raggiunto
		qry1 = "SELECT count(*) from usr_users WHERE username = '" + dati["user"]["username"] + " 'AND chat_id = '" + dati["user"]["chat_id"] + "' AND id_service = (SELECT id from ser_services where code = '" + dati["service"] +"')"
		cond1 = query(qry1)[0][0]
		qry2 = "SELECT count(*) from ser_services where code = '" + dati["service"] + "'"
		cond2 = query(qry2)[0][0]
		qry3 = "SELECT count(*) from par_parameters pp where pp.code = 'MAX_USERS' and CAST(pp.value AS INTEGER) > (SELECT count(*) from usr_users uu )"
		cond3 = query(qry3)[0][0]
		if cond1 == 0 and cond2 != 0 and cond3 != 0:	
			#check se il servizio è censito e se il numero massimo di utenti è raggiunto
			txt = "INSERT INTO usr_users(username, chat_id, id_service,insert_date) Values ('" + dati["user"]["username"] + "', '" + dati["user"]["chat_id"] + "', " + "(SELECT id from ser_services where code = '" + dati["service"] + "'), SYSDATE())"
			out = insert(txt)
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
	return makeResponse(status, generateAnswer(ws, code), code)

@app.route('/servizi', methods = ['GET'])
def GetServices():
	code = 500
	ws = '/servizi'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')    # Bearer YourTokenHere
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			#frase = 'Servizi disponibili: \n'
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.description as Tipo, pp.value as Url FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id;" 
			servizi = query(txt)
			ans = generateAnswer('/servizi', 200)
			header = ans.split('[')[0]
			frase = header + '\n'
			tail = ans.split(']')[1]
			body = ans.split('[')[1].split(']')[0]
			for s in servizi:
				row = body.replace('$tab1', s[0])
				row = row.replace('$tab2', s[2])
				frase += row
				frase += '\n'
			code = auth
			status = 'ok'
		else:
			frase = generateAnswer('/servizi', 401)
			code = auth
			status = 'ko'
	except Exception as e:
		frase = generateAnswer('/servizi', 500)
		status = 'ko'
		code = 500
		logger.error(e)
	return makeResponse(status, frase, code)

@app.route('/spegni', methods = ['GET', 'POST'])
def TurnOff():
	code = 500
	ws = 'spegni'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			uri = '/stop'
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id where ssa2.code <> 'MSG';" 
			servizi = query(txt)
			responses = ''
			for s in servizi:
				url = s[3] + uri
				try:
					r = requests.get(url)
					stato = generateAnswer('/spegni', r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				except:
					stato = generateAnswer('/spegni', 500, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				responses += stato  
			shutdown_server()
			re = responses
			status = 'ok'
			code = 200
		else:
			re = generateAnswer('/spegni', 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		re = generateAnswer('/spegni', 500)
		logger.error(e)
	return makeResponse(status, re, code)

@app.route('/', methods = ['GET'])
def HelloWorld():
	return 'Hello World'

@app.route('/gradi', methods = ['GET'])
def GetDegMotor():
	code = 500
	ws = '/gradi'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/getdeg'
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';"
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					r = requests.get(url)
					resp = str(json.loads(r.text)['response'])
					stato = generateAnswer('/gradi', r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato = stato.replace('$val2', resp)
					stato += '\n'
	
				except:
					stato = generateAnswer('/gradi', 500, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				responses += stato
				status = 'ok'
				code = 200
		else:
			stato = generateAnswer('/gradi', 401)
			responses = stato
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		stato = generateAnswer('/gradi', 500)
		responses = stato
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/vaiazero', methods = ['POST'])
def Go2ZeroMotor():
	code = 500
	ws = '/vaiazero'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/tozero'
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					r = requests.post(url)
					resp = str(json.loads(r.text)['response'])
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				except:
					stato = generateAnswer('/vaiazero', 500, s[4])
					stato = stato.replace('$val1', s[0])
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer('/vaiazero', 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer('/vaiazero', 500)
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/setzero', methods = ['POST'])
def SetZeroMotor():
	code = 500
	ws = '/setzero'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')    # Bearer YourTokenHere
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/setzero'
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					r = requests.post(url)
					resp = str(json.loads(r.text)['response'])
					stato = generateAnswer('/setzero', r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				except:
					stato = generateAnswer('/setzero', 500, s[4])
					stato = stato.replace('$val1', s[0])
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer('/setzero', 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = "Errore generico"
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/ruota', methods = ['POST'])
def Rotate():
	code = 500
	ws = '/ruota'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			#controllo sul chat id se verificato
			commands = testo.split()
			deg = int(commands[1])
			uri = '/steps'
			#eventualmente gestire il servizio
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				myobj = {'deg': deg, 'sender': chat}
				r = requests.post(url, json = myobj)
				t = generateAnswer('/ruota', r.status_code, s[4])
				t = t.replace('$val1', str(json.loads(r.text)['response']))
				t = t.replace('$val2', s[1])
				t += '\n'
				responses += t
			status = 'ok' 
			code = 200
		else:
			status = 'ko'
			resonses = generateAnswer('/ruota', 401)
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		resonses = generateAnswer('/ruota', 500)
		logger.error(e)		
	return makeResponse(status, responses, code)

@app.route('/setlimiti', methods = ['POST'])
def SetLimits():
	code = 500
	ws = '/setlimiti'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/setlimits'
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					txt = "SELECT wl.code, wl.description FROM ws_labes wl join ws_microservices wm on wl.id_websevice = wm.ID where wm.code ='" + ws + "';"
					label = query(txt)
					dictLabel = {key:rest for key, *rest in label}
					dx = testo.lower().split(dictLabel['dx'].lower())[1].strip().split(' ')[0].strip()
					sx = testo.lower().split(dictLabel['sx'].lower())[1].strip().split(' ')[0].strip()
					myobj = {'limits': {'right': dx, 'left': sx}, 'sender': chat}
					r = requests.post(url, json = myobj)
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				except:
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/setlimitedx', methods = ['POST'])
def SetRightLimit():
	code = 500
	ws = '/setlimitedx'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/setrightlimits'
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			l = testo.split()[1]
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					myobj = {'limit': l, 'sender': chat}
					r = requests.post(url, json = myobj)
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato = stato.replace('$val2', l)
					stato += '\n'
				except:
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/setlimitesx', methods = ['POST'])
def SetLeftLimit():
	code = 500
	ws = '/setlimitesx'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')    # Bearer YourTokenHere
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/setleftlimits'
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			l = testo.split()[1]
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					myobj = {'limit': l, 'sender': chat}
					r = requests.post(url, json = myobj)
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato = stato.replace('$val2', l)
					stato += '\n'
				except:
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/getlimiti', methods = ['GET'])
def GetLimits():
	code = 500
	ws = '/getlimiti'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')    # Bearer YourTokenHere
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/getlimits'
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';"
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					r = requests.get(url)
					resp = json.loads(r.text)['response']
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato = stato.replace('$val2', str(resp['right']))
					stato = stato.replace('$val3', str(resp['left']))
					stato += '\n'
				except:
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/resetlimiti', methods = ['DELETE'])
def ResetLimits():
	code = 500
	ws = '/resetlimiti'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/dellimits'
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					r = requests.delete(url)
					#resp = str(json.loads(r.text)['response'])
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				except:
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/comunicazioni', methods = ['POST'])
def Broadcast():
	code = 500
	ws = '/comunicazioni'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/broadcastMsg'
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			words = testo.split()
			words.pop(0)
			l = " ".join(words)
			#lavorare sul database
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';"
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					#gestire il messaggio in broadcast
					#vanno presi gli utenti il problema sarà prendere tutta la colonna in una lista
					txt = "SELECT uu.chat_id from usr_users uu where uu.id_service = " + str(s[4])
					users = query(txt)
					usr = [u[0] for u in users]
					txt = "SELECT uu.username from usr_users uu where uu.chat_id = '" + chat + "'"
					userSender = query(txt)
					#scrivere che l'username di chi ha inviato ha scritto cose. Magari usa le label
					#gestire le label
					myobj = {'text': l, 'users': usr}
					r = requests.post(url, json = myobj)
					#resp = str(json.loads(r.text)['response'])
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato = stato.replace('$val2', l)
					stato += '\n'

				except Exception as e:
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
					logger.error(e)
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/alert', methods = ['POST'])
def Alert():
	code = 500
	ws = '/alert'
	try:
		auth=200
		if auth == 200:
			responses = ''
			uri = '/broadcastVideo'
			uriAlert = '/broadcastMsg'
			file = request.files['media']
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';"
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				urlAlert = s[3] + uriAlert
				try:
					#gestire il messaggio in broadcast
					#vanno presi gli utenti il problema sarà prendere tutta la colonna in una lista
					txt = "SELECT uu.chat_id from usr_users uu where uu.id_service = " + str(s[4])
					users = query(txt)
					txt = "SELECT wl.code, wl.description FROM ws_labels wl join ws_microservices wm on wl.id_microservice = wm.ID where wm.code ='" + ws + "';"
					label = query(txt)
					dictLabel = {key:rest for key, *rest in label}
					usr = [u[0] for u in users]
					myobj = {'users': usr}
					files = {'media':file, 'data': json.dumps(myobj)}
					r = requests.post(url, files=files)
					myobj = {'text': dictLabel['alert'][0], 'users': usr}
					r2 = requests.post(urlAlert, json = myobj)
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				except Exception as e:
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
					logger.error(e)
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger.error(e)
	return makeResponse(status, responses, code) 


#gestire lo start lo stop con un broadcast message
@app.route('/start', methods = ['POST'])
def Start():
	code = 500
	ws = '/start'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/start'
			uriBroad = '/broadcastMsg'
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					r = requests.post(url)
					resp = str(json.loads(r.text)['response'])
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				except Exception as e:
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
					logger.error(e)
				responses += stato
				status = 'ok'
				code = 200
			broadObj = {'text': stato, 'sender':chat}
			rBroad = requests.post('http://localhost:5001/comunicazioni', json = broadObj)
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger.error(e)
	return makeResponse(status, responses, code) 

@app.route('/stop', methods = ['POST'])
def Stop():
	code = 500
	ws = '/stop'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/stop'
			uriBroad = '/broadcastMsg'
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					r = requests.post(url)
					resp = str(json.loads(r.text)['response'])
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				except:
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
				responses += stato
				status = 'ok'
				code = 200
			broadObj = {'text': stato, 'sender':chat}
			rBroad = requests.post('http://localhost:5001/comunicazioni', json = broadObj)
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger(e)
	return makeResponse(status, responses, code)

@app.route('/foto', methods = ['POST'])
def Foto():
	code = 500
	ws = '/foto'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')    # Bearer YourTokenHere
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			uri = '/pic'
			uriPic = '/broadcastPic'
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				try:
					r = requests.get(url)
					resp = BytesIO(r.content)
					usr = chat
					#qua va bene per prendere l'url mi devo mettere una query custom per prendere l'url del servizio di comunicazione dell'utente
					#query abbastanza facile
					usrSearchQry = "select pp.value FROM usr_users uu join ser_services ss on uu.id_service = ss.ID join par_parameters pp on ss.id_url = pp.id where uu.chat_id = '" + usr +"'"
					usrSearch = query(usrSearchQry)
					urlImg = usrSearch[0][0] + uriPic		
					myobj = {'users': [usr]}
					files = {'media':resp, 'data': json.dumps(myobj)}
					r2 = requests.post(urlImg, files=files)
					stato = generateAnswer(ws, r.status_code, s[4])
					stato = stato.replace('$val1', s[0])
					stato += '\n'
				except Exception as e:
					logger.error(e)
					stato = generateAnswer(ws, 500, s[4])
					stato = stato.replace('$val1', s[0])
				responses += stato
				status = 'ok'
				code = 200
		else:
			responses = generateAnswer(ws, 401)
			status = 'ko'
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		responses = generateAnswer(ws, 500)
		logger.error(e)
	return makeResponse(status, responses, code) 


@app.route('/admin', methods = ['GET'])
def Admin():
	code = 500
	ws = '/admin'	
	try:
		headers = request.headers
		bearer = headers.get('Authorization')    # Bearer YourTokenHere
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			#migliorare
			txt = "SELECT wm.code as comando, wm.description, nvl(ss.description, '') FROM ws_microservices wm left outer JOIN ser_services ss on wm.id_service = ss.id left outer JOIN rol_microservices rm on rm.id_microservice = wm.id left outer JOIN rol_roles rr on rr.id = rm.id_role WHERE rr.code = 'admin' and wm.fl_deleted = 0 and (ss.fl_deleted = 0 or ss.fl_deleted  is null) and wm.id not in (select rm2.id_microservice from rol_microservices rm2 where rm2.id_role <> rr.id)"
			servizi = query(txt)
			ans = generateAnswer('/servizi', 200)
			header = ans.split('[')[0]
			frase = header + '\n'
			tail = ans.split(']')[1]
			body = ans.split('[')[1].split(']')[0]
			for s in servizi:
				row = body.replace('$tab1', s[0])
				row = row.replace('$tab2', s[1])
				row = row.replace('$tab3', s[2])
				frase += row
				frase += '\n'
			code = auth
			status = 'ok'
		else:
			frase = generateAnswer('/admin', 401)
			code = auth
			status = 'ko'
	except Exception as e:
		frase = generateAnswer('/admin', 500)
		status = 'ko'
		code = 500
		logger.error(e)
	return makeResponse(status, frase, code)

@app.route('/soglia', methods = ['POST'])
def Soglia():
	code = 500
	ws = '/soglia'
	try:
		headers = request.headers
		bearer = headers.get('Authorization')
		token = bearer.split()[1]
		auth = checkBearer(token, ws)
		if auth == 200:
			responses = ''
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			#controllo sul chat id se verificato
			commands = testo.split()
			th = commands[1]
			uri = '/tresh'
			#eventualmente gestire il servizio
			txt = "SELECT ss.description as Servizio, ss.description as Codice, ssa2.code as Tipo, pp.value as Url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';" 
			servizi = query(txt)
			for s in servizi:
				url = s[3] + uri
				myobj = {'threshold': th, 'sender': chat}
				r = requests.post(url, json = myobj)
				t = generateAnswer(ws, r.status_code, s[4])
				t = t.replace('$val1', str(th))
				t = t.replace('$val2', s[1])
				t += '\n'
				responses += t
			status = 'ok' 
			code = 200
		else:
			status = 'ko'
			resonses = generateAnswer(ws, 401)
			code = 401
	except Exception as e:
		status = 'ko'
		code = 500
		resonses = generateAnswer(ws, 500)
		logger.error(e)		
	return makeResponse(status, responses, code)

@app.errorhandler(404)
#mettere questo servizio come gli altri
def NotFound(error):
	print('\n404\n')
	try:
		headers = request.headers
		bearer = headers.get('Authorization') 
		token = bearer.split()[1]
		auth = checkBearer(token)
		if auth == 200:
			pageName =  request.args.get('url')
			code = 404
			resp = 'Funzione non disponibile'
			serv = 'Servizi disponibili: \n'
			txt = "SELECT ss.description as Servizio, ss.code as Codice, ssa2.code as Tipo, pp.value as Url FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id;" 
			servizi = query(txt)
			for s in servizi:
				serv += s[0]
				serv += ', tipologia: '
				serv += s[2]
				serv += '\n'
			resp = resp + '\n' + '\n' + serv
			status = 'ok'
		else:
			code = 401
			status = 'ko'
			resp = 'Non autorizzato'
		myResponse = make_response(resp)
		myResponse.status_code = code
	except Exception as e:
		status = 'ko'
		code = 500
		resp = "Errore generico"
		logger.error(e)
	return makeResponse(status, resp, code)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)