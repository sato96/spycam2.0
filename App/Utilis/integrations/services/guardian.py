import requests
import json
from Utilis.integrations.response.ResponseFactory import ResponseFactory
from Utilis.integrations.services.ui import Communications
from io import BytesIO
import traceback

class Monitoring(object):

	@staticmethod
	def start(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/start'
		uriBroad = '/broadcastMsg'
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		testo = dati['text']
		chat = dati['sender']
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';"
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				r = requests.post(url)
				resp = str(json.loads(r.text)['response'])
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato += '\n'
			except Exception as e:
				stato = ResponseFactory.generateAnswer(ws, 500, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				logger.error(e)
			responses += stato
			status = 'ok'
			code = 200
		broadObj = {'text': stato, 'sender':chat, 'toSender': False}
		rBroad = Communications.broadcast('/comunicazioni',broadObj,connector, logger)
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def stop(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/stop'
		uriBroad = '/broadcastMsg'
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		testo = dati['text']
		chat = dati['sender']
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';"
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				r = requests.post(url)
				resp = str(json.loads(r.text)['response'])
				stato = ResponseFactory.generateAnswer(ws, r.status_code,connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato += '\n'
			except Exception as e:
				stato = ResponseFactory.generateAnswer(ws, 500,connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				logger.error(e)
			responses += stato
			status = 'ok'
			code = 200
		broadObj = {'text': stato, 'sender':chat, 'toSender': False}
		rBroad = Communications.broadcast('/comunicazioni',broadObj,connector, logger)
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def trashold(ws,request,connector,logger, serv = ""):
		responses = ''
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		testo = dati['text']
		chat = dati['sender']
		#controllo sul chat id se verificato
		commands = testo.split()
		th = int(commands[1])
		uri = '/tresh'
		#eventualmente gestire il servizio
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where  wm.fl_deleted = 0 and wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';" 
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				myobj = {'threshold': th, 'sender': chat}
				r = requests.post(url, json = myobj)
				t = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				t = t.replace('$val2', str(json.loads(r.text)['response']))
				t = t.replace('$val1', s['service'])
				t += '\n'
				responses += t
			except Exception as e:
				stato = ResponseFactory.generateAnswer(ws, 500,connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				logger.error(e)
				responses += stato
		status = 'ok' 
		code = 200
		return ResponseFactory.makeResponse(status, responses, code)



class MultimediaAlert(object):

	@staticmethod
	def photo(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/pic'
		uriPic = '/broadcastPic'
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		testo = dati['text']
		chat = dati['sender']
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';"
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				r = requests.get(url)
				resp = BytesIO(r.content)
				usr = chat
				usrSearchQry = "select pp.value FROM usr_users uu join ser_services ss on uu.id_service = ss.ID join par_parameters pp on ss.id_url = pp.id where uu.chat_id = '" + usr +"'"
				usrSearch = connector.query(usrSearchQry)
				urlImg = usrSearch[0]['value'] + uriPic		
				myobj = {'users': [usr]}
				files = {'media':resp, 'data': json.dumps(myobj)}
				r2 = requests.post(urlImg, files=files)
				stato = ResponseFactory.generateAnswer(ws, r.status_code,connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato += '\n'
			except Exception as e:
				logger.error(e)
				stato = ResponseFactory.generateAnswer(ws, 500, connector,s['id'])
				stato = stato.replace('$val1', s['service'])
			responses += stato
		status = 'ok'
		code = 200
		return ResponseFactory.makeResponse(status, responses, code)