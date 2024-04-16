import requests
import json
from Utilis.integrations.response.ResponseFactory import ResponseFactory
import traceback

class RotationServices(object):
	@staticmethod
	def getDegMotor(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/getdeg'
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.fl_deleted = 0 and wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';"
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				r = requests.get(url)
				resp = str(json.loads(r.text)['response'])
				stato = ResponseFactory.generateAnswer(ws, r.status_code,connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato = stato.replace('$val2', resp)
				stato += '\n'
			except Exception as e:
				logger.error(e)
				stato = ResponseFactory.generateAnswer(ws, 500, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato += '\n'
			responses += stato
			status = 'ok'
			code = 200
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def go2ZeroMotor(ws,request, connector, logger, serv = ""):
		responses = ''
		uri = '/tozero'
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id  FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where  wm.fl_deleted = 0 and wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';" 
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				r = requests.post(url)
				resp = str(json.loads(r.text)['response'])
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector,s['id'])
				stato = stato.replace('$val1', s['service'])
				stato += '\n'
			except Exception as e:
				stato = ResponseFactory.generateAnswer(ws, 500, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
			responses += stato
			status = 'ok'
			code = 200
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def rotate(ws,request,connector,logger, serv = ""):
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
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where  wm.fl_deleted = 0 and wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';" 
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			myobj = {'deg': deg, 'sender': chat}
			r = requests.post(url, json = myobj)
			t = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
			t = t.replace('$val1', str(json.loads(r.text)['response']))
			t = t.replace('$val2', s['service'])
			t += '\n'
			responses += t
		status = 'ok' 
		code = 200
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def setZeroMotor(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/setzero'
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where  wm.fl_deleted = 0 and wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';" 
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
				logger.error(e)
				stato = ResponseFactory.generateAnswer(ws, 500, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
			responses += stato
			status = 'ok'
			code = 200
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def setLimits(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/setlimits'
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		testo = dati['text']
		chat = dati['sender']
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';" 
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				txt = "SELECT wl.code, wl.description FROM ws_labels wl join ws_microservices wm on wl.id_microservice = wm.ID where wm.code ='" + ws + "';"
				label = connector.query(txt)
				dictLabel = {row['code']:row['description'] for row in label}
				dx = testo.lower().split(dictLabel['dx'].lower())[1].strip().split(' ')[0].strip()
				sx = testo.lower().split(dictLabel['sx'].lower())[1].strip().split(' ')[0].strip()
				myobj = {'limits': {'right': dx, 'left': sx}, 'sender': chat}
				r = requests.post(url, json = myobj)
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato += '\n'
			except Exception as e:
				logger.exception(traceback.format_exc())
				stato = ResponseFactory.generateAnswer(ws, 500, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
			responses += stato
			status = 'ok'
			code = 200
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def setRightLimit(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/setrightlimits'
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		testo = dati['text']
		chat = dati['sender']
		l = testo.split()[1]
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';" 
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				myobj = {'limit': l, 'sender': chat}
				r = requests.post(url, json = myobj)
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				stato = stato.replace('$val1', s["service"])
				stato = stato.replace('$val2', l)
				stato += '\n'
			except:
				stato = generateAnswer(ws, 500, s['id'])
				stato = stato.replace('$val1', s['service'])
			responses += stato
			status = 'ok'
			code = 200
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def setLeftLimit(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/setleftlimits'
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		testo = dati['text']
		chat = dati['sender']
		l = testo.split()[1]
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';" 
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				myobj = {'limit': l, 'sender': chat}
				r = requests.post(url, json = myobj)
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				stato = stato.replace('$val1', s["service"])
				stato = stato.replace('$val2', l)
				stato += '\n'
			except:
				stato = generateAnswer(ws, 500, s['id'])
				stato = stato.replace('$val1', s['service'])
			responses += stato
			status = 'ok'
			code = 200
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def getLimits(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/getlimits'
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';" 
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				r = requests.get(url)
				resp = json.loads(r.text)['response']
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato = stato.replace('$val2', str(resp['right']))
				stato = stato.replace('$val3', str(resp['left']))
				stato += '\n'
			except:
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
			responses += stato
			status = 'ok'
			code = 200
		return ResponseFactory.makeResponse(status, responses, code)

	@staticmethod
	def resetLimits(ws, request, connector, logger, serv = ""):
		responses = ''
		uri = '/dellimits'
		txt = "SELECT ss.description as service, ss.code as code, ssa2.code as type, pp.value as url, ss.id FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id JOIN ws_microservices wm on ss.id = wm.id_service where wm.code ='" + ws + "' and ss.code like '%"+ str(serv) + "%';" 
		servizi = connector.query(txt)
		for s in servizi:
			url = s['url'] + uri
			try:
				r = requests.delete(url)
				resp = json.loads(r.text)['response']
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
				stato += '\n'
			except:
				stato = ResponseFactory.generateAnswer(ws, r.status_code, connector, s['id'])
				stato = stato.replace('$val1', s['service'])
			responses += stato
			status = 'ok'
			code = 200
		return ResponseFactory.makeResponse(status, responses, code)
