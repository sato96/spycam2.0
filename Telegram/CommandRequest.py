
import requests
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from LoginTelegram import LoginHandler
login = LoginHandler.login

class CommandRequests(object):

	@staticmethod
	def fullCommand(username, chatId, text, baseUrl):
		log, bearer = login(username,chatId, baseUrl)
		if bearer != 'ko':
			#sarebbe meglio non mandare un'altra request ma vabe
			user_says = text.split(' ')[0]
			url = baseUrl + user_says
			headers = {'Content-Type':'application/json','Authorization': 'Bearer {}'.format(bearer)}
			data = {'text': text, 'sender': str(chatId)}
			r = requests.post(url, headers=headers, json = data)
			if r.status_code == 200:
				resp = str(json.loads(r.text)['response'])
			else:
				resp = str(json.loads(r.text)['response'])
		else:
			resp =  log
		return resp

	@staticmethod
	def getCommand(username, chatId, text, baseUrl):
		log, bearer = login(username,chatId, baseUrl)
		if bearer != 'ko':
			#sarebbe meglio non mandare un'altra request ma vabe
			user_says = text.split(' ')[0]
			url = baseUrl + user_says
			headers = {'Content-Type':'application/json','Authorization': 'Bearer {}'.format(bearer)}
			r = requests.get(url, headers=headers)
			if r.status_code == 200:
				resp = str(json.loads(r.text)['response'])
			else:
				resp = str(json.loads(r.text)['response'])
		else:
			resp =  log
		return resp

	@staticmethod
	def deleteCommand(username, chatId, text, baseUrl):
		log, bearer = login(username,chatId, baseUrl)
		if bearer != 'ko':
			#sarebbe meglio non mandare un'altra request ma vabe
			user_says = text.split(' ')[0]
			url = baseUrl + user_says
			headers = {'Content-Type':'application/json','Authorization': 'Bearer {}'.format(bearer)}
			r = requests.delete(url, headers=headers)
			if r.status_code == 200:
				resp = str(json.loads(r.text)['response'])
			else:
				resp = str(json.loads(r.text)['response'])
		else:
			resp =  log
		return resp

	@staticmethod
	def paramCommand(username, chatId, text, baseUrl):
		log, bearer = login(username,chatId, baseUrl)
		if bearer != 'ko':
			#sarebbe meglio non mandare un'altra request ma vabe
			user_says = text.split(' ')[0]
			url = baseUrl + user_says
			headers = {'Content-Type':'application/json','Authorization': 'Bearer {}'.format(bearer)}
			data = {'text': text, 'sender': str(chatId)}
			r = requests.post(url, headers=headers, json = data)
			if r.status_code == 200:
				resp = str(json.loads(r.text)['response'])
			else:
				resp = str(json.loads(r.text)['response'])
		else:
			resp =  log
		return resp

	@staticmethod
	def services(username, chatId, text, baseUrl):
		log, bearer = login(username,chatId, baseUrl)
		if bearer != 'ko':
			user_says = text.split(' ')[0]
			url = baseUrl + user_says
			headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(bearer)}
			r = requests.get(url, headers=headers)
			if r.status_code == 200:
				resp = str(json.loads(r.text)['response'])
			else:
				resp = str(json.loads(r.text)['response'])
		else:
			resp = log
		return resp, json.loads(r.text)['data']
	
	@staticmethod
	def microS(service, bearer, baseUrl):
		url = baseUrl + service
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(bearer)}
		r = requests.get(url, headers=headers)
		if r.status_code == 200:
			resp = str(json.loads(r.text)['response'])
		else:
			resp = str(json.loads(r.text)['response'])
		keyboard = []
		d = json.loads(r.text)['data']
		with open('Labels.json') as f:
			j = json.load(f)
			back = j["back"]
			end = j["end"]
		r = len(d) % 2
		for s in range(0, len(d) - r, 2):
			call0 = d[s]['code'] + '?' + service.split('?')[1]
			call1 = d[s + 1]['code'] + '?' + service.split('?')[1]
			keyboard.append([InlineKeyboardButton(d[s]['microservice'], callback_data=call0),
							InlineKeyboardButton(d[s + 1]['microservice'], callback_data=call1)])
		if r == 1:
			call = d[len(d) - 1]['code'] + '?' + service.split('?')[1]
			keyboard.append([InlineKeyboardButton(d[len(d) - 1]['microservice'], callback_data=call)])
		keyboard.append([InlineKeyboardButton(back, callback_data='/back'),InlineKeyboardButton(end, callback_data='/end')])
		reply_markup = InlineKeyboardMarkup(keyboard)
		return resp, reply_markup


