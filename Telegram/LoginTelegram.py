
import requests
import json


class LoginHandler(object):


	@staticmethod
	def login(user, chat_id, base_url):
		url = base_url + '/login'
		j = {"user": user, "chat_id": str(chat_id)}
		try:
			r = requests.post(url, json = j)
			if r.status_code == 200:
				token = json.loads(r.text)['data']['token']
				resp = json.loads(r.text)['response']
			else:
				token =  'ko'
				resp = json.loads(r.text)['response']
		except Exception as e:
			#logger.error(e)
			resp = 'ko'
			token = 'ko'
		return resp,token