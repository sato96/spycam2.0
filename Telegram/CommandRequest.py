
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


