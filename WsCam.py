
from CameraModule import spycam
from flask import Flask,make_response, request, Response, send_file
from flask_cors import cross_origin
from CameraModule import spycam
import json
import threading
import time
from io import BytesIO
import logging

def shutdown_server():
	func = request.environ.get('werkzeug.server.shutdown')
	if func is None:
		raise RuntimeError('Not running with the Werkzeug Server')
	func()

def makeResponse(status, response, code):
	resp = {"status": status, "response": response}
	myResponse = make_response(json.dumps(resp))
	myResponse.status_code = code
	return myResponse


def makeImageResponse(file):	  
	img_binary_data = file.getvalue()
	# Imposta eventuali altre intestazioni della risposta
	myResponse = Response(img_binary_data, mimetype='image/jpg')
	return myResponse



logging.basicConfig(filename='tmp/wsPicamera.log', level=logging.DEBUG, 
					format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)
app = Flask('Cam')
cam = spycam()


@app.route('/ko')
def ko():
	shutdown_server()
	return 'turn off'

@app.route('/')
def hello_world():
	return 'Hello from Flask!!'


@app.route('/pic', methods = ['GET'])
def pic():
	code = 200
	status = 'ok'
	try:	
		image = cam.pic()
		resp = BytesIO()
		image.save(resp, 'jpeg')
		status = 'ok'
		r = makeImageResponse(resp)
	except Exception as e:
		logger.error(e)
		code = 500
		resp = 'Error ' + str(e) 
		status = 'ko'
		r = makeResponse(status, resp, code)
	return r

@app.route('/parameters', methods = ['GET'])
def parameters():
	code = 200
	status = 'ok'
	try:
		resp = cam.getParameters()
		status = 'ok'
	except Exception as e:
		logger.error(e)
		code = 500
		resp = 'Error ' + str(e) 
		status = 'ko'
	return makeResponse(status, resp, code)


@app.route('/start', methods = ['POST'])
def start():
	code = 200
	status = 'ok'
	try: 
		
		t0 = threading.Thread(target = cam.start)
		t0.start()
		resp = 'ok'
		status = 'ok'
	except Exception as e:
		logger.error(e)
		code = 500
		resp = 'Error ' + str(e) 
		status = 'ko'
	return makeResponse(status, resp, code)

@app.route('/stop', methods = ['POST','GET'])
def stop():
	code = 200
	status = 'ok'
	try:
		
		cam.stop()
		resp = 'ok'
		status = 'ok'
	except Exception as e:
		logger.error(e)
		code = 500
		resp = 'Error ' + str(e) 
		status = 'ko'
	return makeResponse(status, resp, code)


@app.route('/tresh', methods = ['POST'])
def tresh():
	code = 200
	status = 'ok'
	try:
		
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		b = dati['threshold']
		cam.thresh = b
		resp = 'ok'
		status = 'ok'
	except Exception as e:
		logger.error(e)
		code = 500
		resp = 'Error ' + str(e) 
		status = 'ko'
	return makeResponse(status, resp, code)

@app.route('/reload', methods = ['POST'])
def realod():
	code = 200
	status = 'ok'
	try:
		cam.realodConfig()
		resp = 'ok'
		status = 'ok'
	except Exception as e:
		logger.error(e)
		code = 500
		resp = 'Error ' + str(e) 
		status = 'ko'
	return makeResponse(status, resp, code)

if __name__ == '__main__':
	service_code = 'picamerav2noIR'
	app.run(host='0.0.0.0', port=5004, debug=True)
