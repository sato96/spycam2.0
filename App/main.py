from flask import Flask, request
from flask_cors import cross_origin
import requests
from Utilis.db.MysqlConnector import MysqlConnector
from Utilis.integrations.ws.WebServicesFactory import WebServiceFactory
from Utilis.integrations.response.ResponseFactory import ResponseFactory
from Utilis.integrations.services.motor import RotationServices
from Utilis.integrations.services.guardian import Monitoring
from Utilis.integrations.services.guardian import MultimediaAlert
from Utilis.integrations.services.ui import Communications
from Utilis.system.SysServices import SystemServices
import json
from io import BytesIO
import logging
from SysHandler import SystemHandler as sys


logging.basicConfig(filename='tmp/mainApp.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger=logging.getLogger(__name__)
#mettere il puntamento in json di configurazione
connector = MysqlConnector('localhost','spyCam','SPY_CAM', 'spycam', logger)
app = Flask('Main')

#ws di login per il bearer e ws di controllo del bearer. Mettere il bearer con una scadenza
@app.route('/login', methods = ['POST'])
def Login():
	ws = '/login'
	r = WebServiceFactory.login(ws, request, connector, logger)
	return r

@app.route('/registrati', methods = ['POST'])
def SignIn():	
	ws = '/registrati'
	r = WebServiceFactory.signIn(ws, request, connector, logger)
	return r


@app.route('/gradi', methods = ['GET'])
def GetDegMotor():
	ws = '/gradi'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, RotationServices.getDegMotor)
	return r

@app.route('/vaiazero', methods = ['POST'])
def Go2ZeroMotor():
	ws = '/vaiazero'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, RotationServices.go2ZeroMotor)
	return r

@app.route('/ruota', methods = ['POST'])
def Rotate():
	ws = '/ruota'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, RotationServices.rotate)
	return r

@app.route('/setzero', methods = ['POST'])
def SetZeroMotor():
	ws = '/setzero'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, RotationServices.setZeroMotor)
	return r

@app.route('/setlimiti', methods = ['POST'])
def SetLimits():
	ws = '/setlimiti'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, RotationServices.setLimits)
	return r

@app.route('/setlimitedx', methods = ['POST'])
def SetRightLimit():
	ws = '/setlimitedx'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, RotationServices.setRightLimit)
	return r

@app.route('/setlimitesx', methods = ['POST'])
def SetLeftLimit():
	ws = '/setlimitesx'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, RotationServices.setLeftLimit)
	return r

@app.route('/getlimiti', methods = ['GET'])
def GetLimits():
	ws = '/getlimiti'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, RotationServices.getLimits)
	return r

@app.route('/resetlimiti', methods = ['DELETE'])
def ResetLimits():
	ws = '/resetlimiti'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, RotationServices.resetLimits)
	return r

@app.route('/start', methods = ['POST'])
def Start():
	ws = '/start'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, Monitoring.start)
	return r
@app.route('/stop', methods = ['POST'])
def Stop():
	ws = '/stop'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, Monitoring.stop)
	return r

@app.route('/soglia', methods = ['POST'])
def Soglia():
	ws = '/soglia'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, Monitoring.trashold)
	return r

@app.route('/foto', methods = ['POST'])
def Foto():
	ws = '/foto'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, MultimediaAlert.photo)
	return r

@app.route('/comunicazioni', methods = ['POST'])
def Broadcast():
	ws = '/comunicazioni'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, Communications.broadcast)
	return r
@app.route('/alert', methods = ['POST'])
def Alert():
	ws = '/alert'
	try:
		r = Communications.alert(ws, request, connector, logger)
	except Exception as e:
		status = 'ko'
		logger.error(e)
		code = 500
		responses = ResponseFactory.generateAnswer(ws, 500, connector)
		print(traceback.format_exc())
		logger.exception(traceback.format_exc())
		r = ResponseFactory.makeResponse(status, responses, code) 
	return r

@app.route('/servizi', methods = ['GET'])
def GetServices():
	ws = '/servizi'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, SystemServices.getServices)
	return r

@app.route('/microservizi', methods = ['GET'])
def GetMicroServices():
	ws = '/microservizi'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, SystemServices.getMicroServices)
	return r

@app.route('/admin', methods = ['GET'])
def Admin():
	ws = '/admin'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, SystemServices.admin)
	return r

@app.route('/parametrisistema', methods = ['GET'])
def SysParameters():
	ws = '/parametrisistema'
	r = WebServiceFactory.wsHandler(ws, request, connector, logger, SystemServices.sysParams)
	return r




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
