import requests
import json
from Utilis.integrations.response.ResponseFactory import ResponseFactory
from SysHandler import SystemHandler as sys



class SystemServices:

	@staticmethod
	def getServices(ws, request, connector, logger, serv = ""):
		txt = "SELECT ss.description as service, ss.code as code, ssa2.description as type, pp.value as url FROM ser_services ss Join ser_service_areas ssa2 on ss.id_area = ssa2.id join par_parameters pp on ss.id_url = pp.id where ss.fl_deleted = 0;" 
		servizi = connector.query(txt)
		ans = ResponseFactory.generateAnswer(ws, 200, connector)
		header = ans.split('[')[0]
		frase = header + '\n'
		tail = ans.split(']')[1]
		body = ans.split('[')[1].split(']')[0]
		for s in servizi:
			row = body.replace('$tab1', s['service'])
			row = row.replace('$tab2', s['type'])
			frase += row
			frase += '\n'
		code = 200
		status = 'ok'
		return ResponseFactory.makeResponse(status, frase, code, servizi)

	@staticmethod
	def getMicroServices(ws, request, connector, logger, serv = ""):
		if serv == None:
			txt = "SELECT wm.code, wm.description as microservice, nvl(ss.description, '') as service FROM ws_microservices wm left outer JOIN ser_services ss on wm.id_service = ss.id left outer JOIN rol_microservices rm on rm.id_microservice = wm.id left outer JOIN rol_roles rr on rr.id = rm.id_role WHERE rr.code <> 'admin' and wm.fl_deleted = 0 and (ss.fl_deleted = 0 or ss.fl_deleted  is null) and fl_user = 1 Order by nvl(ss.description, ''), wm.code;" 
		else:
			txt = "SELECT wm.code, wm.description as microservice, nvl(ss.description, '') as service FROM ws_microservices wm left outer JOIN ser_services ss on wm.id_service = ss.id left outer JOIN rol_microservices rm on rm.id_microservice = wm.id left outer JOIN rol_roles rr on rr.id = rm.id_role WHERE rr.code <> 'admin' and wm.fl_deleted = 0 and (ss.fl_deleted = 0 or ss.fl_deleted  is null) and fl_user = 1 and ss.code like '%"+ str(serv) + "%' Order by nvl(ss.description, ''), wm.code;" 
		microservizi = connector.query(txt)
		ans = ResponseFactory.generateAnswer(ws, 200, connector)
		header = ans.split('[')[0]
		frase = header + '\n'
		tail = ans.split(']')[1]
		body = ans.split('[')[1].split(']')[0]
		for s in microservizi:
			row = body.replace('$tab1', s['code'])
			row = row.replace('$tab2', s['microservice'])
			row = row.replace('$tab3', s['service'])
			frase += row
			frase += '\n'
		code = 200
		status = 'ok'
		return ResponseFactory.makeResponse(status, frase, code, microservizi)


	@staticmethod
	def admin(ws, request, connector, logger, serv = ""):
		code = 200
		try:
			txt = "SELECT wm.code as command, wm.description, nvl(ss.description, '') as service, wm.id FROM ws_microservices wm left outer JOIN ser_services ss on wm.id_service = ss.id left outer JOIN rol_microservices rm on rm.id_microservice = wm.id left outer JOIN rol_roles rr on rr.id = rm.id_role WHERE rr.code = 'admin' and wm.fl_deleted = 0 and (ss.fl_deleted = 0 or ss.fl_deleted  is null) and wm.fl_user = 1 and wm.id not in (select rm2.id_microservice from rol_microservices rm2 where rm2.id_role <> rr.id)"
			servizi = connector.query(txt)
			ans = ResponseFactory.generateAnswer('/admin', 200, connector)
			header = ans.split('[')[0]
			frase = header + '\n'
			tail = ans.split(']')[1]
			body = ans.split('[')[1].split(']')[0]
			for s in servizi:
				row = body.replace('$tab1', s['command'])
				row = row.replace('$tab2', s['description'])
				row = row.replace('$tab3', s['service'])
				frase += row
				frase += '\n'
			frase += tail
		except Exception as e:
			logger.error(e)
			code = 500
			frase = ResponseFactory.generateAnswer(ws, 500, connector)
		status = 'ok'
		return ResponseFactory.makeResponse(status, frase, code, servizi)

	@staticmethod
	def sysParams(ws, request, connector, logger, serv = ""):
		try:
			ans = ResponseFactory.generateAnswer('/parametrisistema', 200, connector)
			listAns = ans.split(']')
			info = sys.getSystemInfo()
			header = listAns[0].split('[')[0]
			frase1 = header + '\n'
			body = listAns[0].split('[')[1].split(']')[0]
			for key, value in info.items():
				row = body.replace('$tab1', key)
				row = row.replace('$tab2', value)
				frase1 += row
				frase1 += '\n'
			txt = "select pp.description, pp.value FROM par_parameters pp"
			parametri = connector.query(txt)
			header = listAns[1].split('[')[0]
			frase2 = header + '\n'
			body = listAns[1].split('[')[1].split(']')[0]
			for s in parametri:
				row = body.replace('$tab3', s['description'])
				row = row.replace('$tab4', s['value'])
				frase2 += row
				frase2 += '\n'

			txt = "select uu.username, ss.description as service, rr.description as role FROM usr_users uu JOIN ser_services ss on uu.id_service = ss.id JOIN rol_roles rr on uu.`role` = rr.id where uu.fl_deleted = 0	"
			utenti = connector.query(txt)
			header = listAns[2].split('[')[0]
			frase3 = header + '\n'
			body = listAns[2].split('[')[1].split(']')[0]
			for s in utenti:
				row = body.replace('$tab5', s['username'])
				row = row.replace('$tab6', s['service'])
				row = row.replace('$tab7', s['role'])
				frase3 += row
				frase3 += '\n'
			frase = frase1 + frase2 + frase3
			status = 'ok'
			code = 200
		except Exception as e:
			status = 'ko'
			code = 500
			frase = ResponseFactory.generateAnswer(ws, 500, connector)
		return ResponseFactory.makeResponse(status, frase, code)