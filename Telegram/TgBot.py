import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler,filters, ConversationHandler,MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import requests
import json
import threading
from CommandRequest import CommandRequests as com
from LoginTelegram import LoginHandler
login = LoginHandler.login




logging.basicConfig(filename='tmp/botTelegram.log',
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	level=logging.ERROR
)
logger=logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	user = update.effective_user.name 
	chat_id = update.effective_chat.id 
	service = service_code
	url = base_url + '/registrati'
	data = {"user": {"username": user, "chat_id": str(chat_id)}, "service": service}
	r = requests.post(url, json = data)
	if r.status_code == 200:
		await update.message.reply_text(str(json.loads(r.text)['response']))
	elif r.status_code != 500:
		await update.message.reply_text(str(json.loads(r.text)['response']))
	else:
		messageError = 'ko'
		with open('Labels.json') as f:
			infoFromUser = json.load(f)["signInError"]
		await update.message.reply_text(messageError)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
	await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

async def full(update: Update, context: ContextTypes.DEFAULT_TYPE):
	resp = com.fullCommand(update.effective_user.name, update.effective_chat.id, update.message.text, base_url)
	await update.message.reply_text(resp)

async def get(update: Update, context: ContextTypes.DEFAULT_TYPE):
	resp = com.getCommand(update.effective_user.name, update.effective_chat.id, update.message.text, base_url)
	await update.message.reply_text(resp)

async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
	resp = com.deleteCommand(update.effective_user.name, update.effective_chat.id, update.message.text, base_url)
	await update.message.reply_text(resp)
	
async def parz(update: Update, context: ContextTypes.DEFAULT_TYPE):
	resp = com.paramCommand(update.effective_user.name, update.effective_chat.id, update.message.text, base_url)
	await update.message.reply_text(resp)

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	resp, data = com.services(update.effective_user.name, update.effective_chat.id, update.message.text.split(' ')[0] , base_url)
	keyboard = []
	for s in data:
		call = '/microservizi?serv=' + s['code']
		keyboard.append([InlineKeyboardButton(s['service'], callback_data=call)])
	reply_markup = InlineKeyboardMarkup(keyboard)
	await update.message.reply_text(resp, reply_markup=reply_markup)
	return MICROSERVICES


async def ms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	query = update.callback_query
	await query.answer()
	log, bearer = login(update.effective_user.name, update.effective_chat.id, base_url)
	if bearer != 'ko':
		# sarebbe meglio non mandare un'altra request ma vabe
		user_says = query.data
		url = base_url + user_says
		headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(bearer)}
		r = requests.get(url, headers=headers)
		if r.status_code == 200:
			resp = str(json.loads(r.text)['response'])
		else:
			resp = str(json.loads(r.text)['response'])
	else:
		resp = log
	keyboard = []
	d = json.loads(r.text)['data']
	with open('Labels.json') as f:
		j = json.load(f)
		back = j["back"]
	r = len(d) % 2
	for s in range(0, len(d) - r, 2):
		call0 = d[s]['code'] + '?' + query.data.split('?')[1]
		call1 = d[s+1]['code'] + '?' + query.data.split('?')[1]
		keyboard.append([InlineKeyboardButton(d[s]['microservice'], callback_data=call0),
						 InlineKeyboardButton(d[s + 1]['microservice'], callback_data=call1)])
	if r == 1:
		call = d[len(d) - 1]['code'] + '?' + query.data.split('?')[1]
		keyboard.append([InlineKeyboardButton(d[len(d) - 1]['microservice'], callback_data=call)])
	keyboard.append([InlineKeyboardButton(back, callback_data='/back')])
	reply_markup = InlineKeyboardMarkup(keyboard)
	await query.edit_message_text(text=resp, reply_markup=reply_markup)
	return FUNCTIONS

async def funz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	query = update.callback_query
	await query.answer()
	if query.data == '/back':
		text = '/' + service
		resp, data = com.services(update.effective_user.name, update.effective_chat.id, text , base_url)
		keyboard = []
		for s in data:
			call = '/microservizi?serv=' + s['code']
			keyboard.append([InlineKeyboardButton(s['service'], callback_data=call)])
		reply_markup = InlineKeyboardMarkup(keyboard)
		await query.edit_message_text(text=resp, reply_markup = reply_markup)
		return MICROSERVICES
	else:
		command = query.data.split('?')[0].split('/')[1]
		if command in parz_c:
			context.user_data["command"] = query.data
			infoFromUser = 'ko'
			with open('Labels.json') as f:
				j = json.load(f)
				infoFromUser = j["infoFromUser"][command]
			await query.edit_message_text(text=infoFromUser)
			return PARZIAL
		elif command in full_c:
			resp = com.fullCommand(update.effective_user.name, update.effective_chat.id, query.data, base_url)
			await query.edit_message_text(text=resp)
			return ConversationHandler.END
		elif command in get_c:
			resp = com.getCommand(update.effective_user.name, update.effective_chat.id, query.data, base_url)
			await query.edit_message_text(text=resp)
			return ConversationHandler.END
		elif command in del_c:
			resp = com.deleteCommand(update.effective_user.name, update.effective_chat.id, query.data, base_url)
			await query.edit_message_text(text=resp)
			return ConversationHandler.END
		else:
			messageError = 'ko'
			with open('Labels.json') as f:
				infoFromUser = json.load(f)["commandNotFound"]
			error = messageError.replace('$data', query.data)
			await query.edit_message_text(text=error)
			return ConversationHandler.END

async def parziale(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
	"""Stores the info about the user and ends the conversation."""
	text = context.user_data["command"] + ' ' + update.message.text
	resp = com.fullCommand(update.effective_user.name, update.effective_chat.id, text, base_url)
	await update.message.reply_text(resp)
	return ConversationHandler.END









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
		service = config['services']
		token = config['token']
		service_code = config['service_code']
		base_url = config['url']
		avvio = config['avvio']
		f.close()
	except Exception as e:
		logger.error(e)
	MICROSERVICES, FUNCTIONS, PARZIAL= range(3)
	application = Application.builder().token(token).build()
	start_handler = CommandHandler(avvio, start)
	#echo handler posso usarlo per il master per mandare messaggi di testo in broadcast
	echo_handler = CommandHandler('echo', echo)
	#praticamente con questo mi gioco tutti gli handler con parametro
	parz_handler = CommandHandler(parz_c, parz)
	#turn_handler = CommandHandler('contrasto', rotate)
	full_handler = CommandHandler(full_c, full)
	get_handler = CommandHandler(get_c, get)
	del_handler = CommandHandler(del_c, delete)
	serv_handler = CommandHandler(service, services)
	application.add_handler(start_handler)
	#application.add_handler(echo_handler)
	application.add_handler(parz_handler)
	application.add_handler(full_handler)
	application.add_handler(get_handler)
	application.add_handler(del_handler)
	conv_handler = ConversationHandler(
		entry_points=[CommandHandler("servizi", services)],
		states={
			MICROSERVICES: [CallbackQueryHandler(ms, pattern="^/microservizi")],
			FUNCTIONS: [
				CallbackQueryHandler(funz),
			],
			PARZIAL: [MessageHandler(filters.TEXT & ~(filters.COMMAND), parziale),],
		},
		fallbacks=[CommandHandler("servizi", services)],
	)
	# Add ConversationHandler to application that will be used for handling updates
	application.add_handler(conv_handler)
	application.run_polling(allowed_updates=Update.ALL_TYPES)

