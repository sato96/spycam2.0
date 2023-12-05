from flask import Flask, make_response, request
from flask_cors import cross_origin
from motor import MotorStep
import json

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

app = Flask('Motor')
motor = MotorStep([24,25,8,7], "MotorConfig.json")


@app.route('/')
def hello_world():

	return 'Hello from Flask!!'


@app.route('/steps', methods = ['POST'])
def Steps():
	body = request.data
	dati = json.loads(body.decode('utf-8'))
	deg = dati['deg']
	code = 200
	resp = str(deg)
	status = 'ok'
	try:
		resp = motor.Rotation(int(deg))
		#gestire quanti gradi reali ho fatto al limite
		resp = str(resp)
		status = 'ok'
		print(resp)
	except Exception as e:
		print(e)
		code = 500
		resp = 'Error ' + str(e) 
		status = 'ko'
	return makeResponse(status, resp, code)


@app.route('/getdeg', methods = ['GET'])
def GetDeg():
	try:
		resp = motor.GetDeg()
		status = 'ok'
		code = 200
	except Exception as e:
		resp = 'Error'
		print(e)
		status = 'ko'
		code = 500
	return makeResponse(status, resp, code)

@app.route('/tozero', methods = ['POST'])
def ToZero():
	code = 200
	try:
		motor.ToZero()
		resp = 'ok'
		status = 'ok'
		code = 200
	except Exception as e:
		code = 500
		resp = 'Error'
		status = 'ko' 
	return makeResponse(status, resp, code)

@app.route('/setzero', methods = ['POST'])
def SetZero():
	code = 200
	try:
		motor.SetZero()
		resp = 'ok'
		status = 'ok'
		code = 200
	except Exception as e:
		code = 500
		resp = 'Error'
		status = 'ko' 
	return makeResponse(status, resp, code)

@app.route('/setlimits', methods = ['POST'])
def SetLimits():
	code = 200
	try:
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		limits = dati['limits']
		#modificare che se manca uno dei due limiti si tiene il precedente
		print(limits)
		ans = motor.SetLimits(int(limits['right']), int(limits['left']))
		if ans == True:
			resp = 'ok'
			status = 'ok'
			code = 200
		else:
			resp = 'Limits not int'
			status = 'ko'
			code = 422
	except Exception as e:
		code = 500
		resp = 'Error'
		status = 'ko' 
	return makeResponse(status, resp, code)

@app.route('/setrightlimits', methods = ['POST'])
def SetRightLimit():
	code = 200
	try:
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		limit = int(dati['limit'])
		ans = motor.SetRightLimit(limit)
		if ans:
			resp = 'ok'
			status = 'ok'
			code = 200
		else:
			resp = 'Limit not int or right limit not setted'
			status = 'ko'
			code = 422
	except Exception as e:
		code = 500
		resp = 'Error'
		status = 'ko' 
		print(e)
	return makeResponse(status, resp, code)

@app.route('/setleftlimits', methods = ['POST'])
def SetLeftLimit():
	code = 200
	try:
		body = request.data
		dati = json.loads(body.decode('utf-8'))
		limit = int(dati['limit'])
		ans = motor.SetLeftLimit(limit)
		if ans:
			resp = 'ok'
			status = 'ok'
			code = 200
		else:
			resp = 'Limit not int or left limit not setted'
			status = 'ko'
			code = 422
	except Exception as e:
		code = 500
		resp = 'Error'
		status = 'ko' 
	return makeResponse(status, resp, code)

@app.route('/getlimits', methods = ['GET'])
def GetLimits():
	try:
		r = motor.GetLimits()
		print(r)
		resp = r
		print(resp)
		status = 'ok'
		code = 200
	except Exception as e:
		resp = 'Error'
		print(e)
		status = 'ko'
		code = 500
	return makeResponse(status, resp, code)

@app.route('/dellimits', methods = ['DELETE'])
def DelLimits():
	try:
		resp = str(motor.DelLimits())
		status = 'ok'
		code = 200
	except Exception as e:
		resp = 'Error'
		print(e)
		status = 'ko'
		code = 500
	return makeResponse(status, resp, code)


@app.route('/stop', methods = ['POST'])
def Stop():
	code = 200
	try:
		motor.StopMotor()
		shutdown_server()
		resp = 'ok'
		status = 'ok'
		code = 200
	except Exception as e:
		code = 500
		resp = 'Error'
		status = 'ko' 
	return makeResponse(status, resp, code)
if __name__ == '__main__':
	service_code = 'MotorStep'
	app.run(host='0.0.0.0', port=5002, debug=True)