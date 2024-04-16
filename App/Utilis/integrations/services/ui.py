import requests
import json
from Utilis.integrations.response.ResponseFactory import ResponseFactory
from io import BytesIO
import traceback

class Communications(object):

	@staticmethod
	def broadcast(ws, request, connector, logger, serv = ""):
		responses = ''
		uri= '/broadcastMsg'
		if isinstance(request, dict):
			testo = request['text']
			chat = request['sender']
			flToSender = False if request.get('toSender') is None else request.get('toSender')
			l = testo
		else:
			body = request.data
			dati = json.loads(body.decode('utf-8'))
			testo = dati['text']
			chat = dati['sender']
			flToSender = False if dati.get('toSender') is None else dati.get('toSender')
			words = testo.split()
			words.pop(0)
			l = " ".join(words)
			if flToSender == False:
				qry = "SELECT uu.username from usr_users uu where uu.chat_id = '" + chat +  "'"
				userName = connector.query(qry)[0]['username']
				qry = "SELECT wl.code, wl.description FROM ws_labels wl where wl.code = 'sender'"
				l = connector.query(qry)[0]['description'].replace('$val1', userName) + " " + l
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';"
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				#vanno presi gli utenti il problema sarà prendere tutta la colonna in una lista
				if flToSender:
					txt = "SELECT uu.chat_id from usr_users uu where uu.id_service = " + str(s['id'])
				else:
					txt = "SELECT uu.chat_id from usr_users uu where uu.chat_id <> '" + chat +  "' AND uu.id_service = " + str(s['id'])
				users = connector.query(txt)
				usr = [u['chat_id'] for u in users]
				txt = "SELECT uu.username from usr_users uu where uu.chat_id = '" + chat + "'"
				userSender = connector.query(txt)
				#scrivere che l'username di chi ha inviato ha scritto cose. Magari usa le label
				#gestire le label
				myobj = {'text': l, 'users': usr}
				r = requests.post(url, json = myobj)
				#resp = str(json.loads(r.text)['response'])
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato = stato.replace('$val2', l)
				stato += '\n'
			except Exception as e:
				stato = ResponseFactory.generateAnswer(ws, 500,connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				logger.error(e)
			responses += stato
		status = 'ok'
		code = 200
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def alert(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/broadcastVideo'
		uriAlert = '/broadcastMsg'
		file = request.files['media']
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "';"
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			urlAlert = s['url'] + uriAlert
			try:
				txt = "SELECT uu.chat_id from usr_users uu where uu.id_service = " + str(s['id'])
				users = connector.query(txt)
				txt = "SELECT wl.code, wl.description FROM ws_labels wl join ws_microservices wm on wl.id_microservice = wm.ID where wm.code ='" + ws + "';"
				label = connector.query(txt)
				dictLabel = {row['code']:row['description'] for row in label}
				usr = [u['chat_id'] for u in users]
				myobj = {'users': usr}
				files = {'media':file, 'data': json.dumps(myobj)}
				r = requests.post(url, files=files)
				myobj = {'text': dictLabel['alert'], 'users': usr}
				r = requests.post(urlAlert, json = myobj)
				stato = ResponseFactory.generateAnswer(ws, r.status_code,connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato += '\n'
			except Exception as e:
				stato = ResponseFactory.generateAnswer(ws, 500, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				logger.error(e)
			responses += stato
		status = 'ok'
		code = 200
		return ResponseFactory.makeResponse(status, responses, code)