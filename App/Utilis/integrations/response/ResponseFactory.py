
from flask import make_response
import json

class ResponseFactory(object):
	"""docstring for ClassName"""

	@staticmethod	
	def generateAnswer(ws, httpCode, connector, service = None):
		ws = str(ws)
		httpCode = str(httpCode)
		if service == None:
			qry = "Select CASE WHEN count(*) > 0 then wr.`text` ELSE 	(SELECT wr2.text from ws_microservices wm2 JOIn ws_responses wr2 on wm2.id = wr2.id_microservice WHERE wm2.id_service is NULL and wm2.code = '"+ ws + "' and wr2.error_code is null) END as `text`from ws_microservices wm JOIn ws_responses wr on wm.id = wr.id_microservice WHERE wm.id_service is null and wm.code = '" + ws + "' and wr.error_code = " + httpCode
		else:
			service = str(service)
			qry = "Select CASE WHEN count(*) > 0 then wr.`text` ELSE 	(SELECT wr2.text from ws_microservices wm2 JOIn ws_responses wr2 on wm2.id = wr2.id_microservice WHERE wm2.id_service = "+ service + " and wm2.code = '"+ ws + "' and wr2.error_code is null) END as `text`from ws_microservices wm JOIn ws_responses wr on wm.id = wr.id_microservice WHERE wm.id_service = " + service +" and wm.code = '" + ws + "' and wr.error_code = " + httpCode
		ans = connector.query(qry)
		return str(ans[0]['text'])

	@staticmethod	
	def makeResponse(status, response, code, data = {}):
		resp = {"status": status, "response": response, "data": data}
		myResponse = make_response(json.dumps(resp))
		myResponse.status_code = code
		return myResponse
		