import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import requests
import json
import threading



logging.basicConfig(filename='tmp/botTelegram.log',
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.ERROR
)
logger=logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	#manda alle mia api chat id e username e controlla se c'è posto in coda
	user = update.effective_user.name 
	chat_id = update.effective_chat.id 
	service = service_code
	url = base_url + '/registrati'
	data = {"user": {"username": user, "chat_id": str(chat_id)}, "service": service}
	r = requests.post(url, json = data)
	if r.status_code == 200:
		await update.message.reply_text("Benvenuto " + update.effective_user.name +  ", ti contatterò qua!")
	elif r.status_code != 500:
		await update.message.reply_text("Sei già registrato o non puoi reigstrarti")
	else:
		await update.message.reply_text("Errore generico contatta l'admin")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def full(update: Update, context: ContextTypes.DEFAULT_TYPE):
	#chiama il main che poi darà l'ok
	#incollare semplicemente la risposta dal main il bot deve essere stupido
	log, bearer = login(update.effective_user.name,update.effective_chat.id)
	if bearer != 'ko':
		#sarebbe meglio non mandare un'altra request ma vabe
		user_says = update.message.text.split(' ')[0]
		url = base_url + user_says
		headers = {'Content-Type':'application/json','Authorization': 'Bearer {}'.format(bearer)}
		data = {'text': update.message.text, 'sender': str(update.effective_chat.id)}
		r = requests.post(url, headers=headers, json = data)
		if r.status_code == 200:
			resp = str(json.loads(r.text)['response'])
		else:
			resp = str(json.loads(r.text)['response'])
	else:
		resp =  log
	await update.message.reply_text(resp)

async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
	log, bearer = login(update.effective_user.name,update.effective_chat.id)
	if bearer != 'ko':
		#sarebbe meglio non mandare un'altra request ma vabe
		user_says = update.message.text.split(' ')[0]
		url = base_url + user_says
		headers = {'Content-Type':'application/json','Authorization': 'Bearer {}'.format(bearer)}
		r = requests.get(url, headers=headers)
		if r.status_code == 200:
			resp = str(json.loads(r.text)['response'])
		else:
			resp = str(json.loads(r.text)['response'])
	else:
		resp =  log
	await update.message.reply_text(resp)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
	log, bearer = login(update.effective_user.name,update.effective_chat.id)
	if bearer != 'ko':
		#sarebbe meglio non mandare un'altra request ma vabe
		user_says = update.message.text.split(' ')[0]
		url = base_url + user_says
		headers = {'Content-Type':'application/json','Authorization': 'Bearer {}'.format(bearer)}
		r = requests.delete(url, headers=headers)
		if r.status_code == 200:
			resp = str(json.loads(r.text)['response'])
		else:
			resp = str(json.loads(r.text)['response'])
	else:
		resp =  log
	await update.message.reply_text(resp)
async def parz(update: Update, context: ContextTypes.DEFAULT_TYPE):
	#chiama il main che poi darà l'ok
	#incollare semplicemente la risposta dal main il bot deve essere stupido
	log, bearer = login(update.effective_user.name,update.effective_chat.id)
	if bearer != 'ko':
		user_says = update.message.text.split(' ')[0]
		url = base_url + user_says
		headers = {'Content-Type':'application/json','Authorization': 'Bearer {}'.format(bearer)}
		data = {'text': update.message.text, 'sender': str(update.effective_chat.id)}
		r = requests.post(url, headers=headers, json = data)
		if r.status_code == 200:
			resp = str(json.loads(r.text)['response'])
		else:
			resp = str(json.loads(r.text)['response'])
	else:
		resp =  log
	await update.message.reply_text(resp)

def login(user, chat_id):
	url = base_url + '/login'
	j = {"user": user, "chat_id": str(chat_id)}
	try:
		r = requests.post(url, json = j)
		if r.status_code == 200:
			token = json.loads(r.text)['token']
			resp = json.loads(r.text)['response']
		else:
			token =  'ko'
			resp = json.loads(r.text)['response']
	except Exception as e:
		logger.error(e)
		resp = 'ko'
		token = 'ko'
	return resp,token

def makeResponse(status, response, code):
	resp = {"status": status, "response": response}
	myResponse = make_response(json.dumps(resp))
	myResponse.status_code = code
	return myResponse





if __name__ == '__main__':
	#start handler ok,
	# il resto sono comandi la cui risposta va gestita del servizio principale
	#sono tutti command handler semplici ma vanno messi con la tupla
	parz_c = ()
	full_c = ()
	get_c = ()
	del_c = ()
	base_url = ''
	service_code = ''
	token = ''
	avvio = ''
	try:
		f = open('ConfigTelegram.json')
		config = json.load(f)
		parz_c = tuple(config['parz'])
		full_c= tuple(config['full'])
		get_c = tuple(config['get'])
		del_c = tuple(config['delete'])
		token = config['token']
		service_code = config['service_code']
		base_url = config['url']
		avvio = config['avvio']
		f.close()
	except Exception as e:
		logger.error(e)
	application = ApplicationBuilder().token(token).build()
	start_handler = CommandHandler(avvio, start)
	#echo handler posso usarlo per il master per mandare messaggi di testo in broadcast
	echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
	#praticamente con questo mi gioco tutti gli handler con parametro
	parz_handler = CommandHandler(parz_c, parz)
	#turn_handler = CommandHandler('contrasto', rotate)
	full_handler = CommandHandler(full_c, full)
	get_handler = CommandHandler(get_c, get)
	del_handler = CommandHandler(del_c, delete)
	application.add_handler(start_handler)
	application.add_handler(echo_handler)
	application.add_handler(parz_handler)
	application.add_handler(full_handler)
	application.add_handler(get_handler)
	application.add_handler(del_handler)
	application.run_polling()
	t0.start()
