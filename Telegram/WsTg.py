from flask import Flask, make_response, request
from flask_cors import cross_origin
import json
import asyncio
import telegram
import logging

async def sendMessage(txt, chat):
	#rendere configurabile il token
	bot = telegram.Bot(token)
	async with bot:
		await bot.send_message(text=txt, chat_id=chat)
async def sendPicture(pic, chat):
	#rendere configurabile il token
	bot = telegram.Bot(token)
	async with bot:
		await bot.send_photo(photo = pic, chat_id=chat)

async def sendVideo(video, chat):
	#rendere configurabile il token
	bot = telegram.Bot(token)
	async with bot:
		await bot.send_video(video = video, chat_id=chat)

def makeResponse(status, response, code):
	resp = {"status": status, "response": response}
	myResponse = make_response(json.dumps(resp))
	myResponse.status_code = code
	return myResponse



logging.basicConfig(filename='tmp/wsTelegram.log', level=logging.ERROR,
					format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)
with open('ConfigTelegram.json', "r") as file:
	config = json.load(file)
token = config['token']
app = Flask('TelegramBot')


@app.route('/broadcastMsg', methods = ['POST'])
def BroadcastMsg():
	code = 0
	try:
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		testo = dati['text']
		chat = dati['users']
		for usr in chat:
			asyncio.run(sendMessage(testo, usr))
		responses = 'ok'
		status = 'ok'
		code = 200
	except Exception as e:
		status = 'ko'
		code = 500
		responses = 'ko'
		logger.error(e)
	return makeResponse(status, responses, code)

@app.route('/broadcastPic', methods = ['POST'])
def BroadcastPic():
	code = 0
	try:
		img = request.files['media'].read()
		chat = json.loads(request.files['data'].read())['users']
		for usr in chat:
			asyncio.run(sendPicture(img, usr))
		responses = 'ok'
		status = 'ok'
		code = 200
	except Exception as e:
		status = 'ko'
		code = 500
		responses = 'ko'
		logger.error(e)
	return makeResponse(status, responses, code)


@app.route('/broadcastVideo', methods = ['POST'])
def BroadcastVideo():
	code = 0
	try:
		video = request.files['media'].read()
		chat = json.loads(request.files['data'].read())['users']
		for usr in chat:
			asyncio.run(sendVideo(video, usr))
		responses = 'ok'
		status = 'ok'
		code = 200
	except Exception as e:
		status = 'ko'
		code = 500
		responses = 'ko'
		logger.error(e)
	return makeResponse(status, responses, code)

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5003, debug=True)