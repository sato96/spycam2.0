#!/usr/bin/python3

import time
import numpy as np
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from picamera2.outputs import FileOutput
from libcamera import Transform
import threading
import requests
import time
import logging
import json



class spycam(object):
	def __init__(self, th = 7, fileConfig = 'configPicamera.json'):
		#vanno gestiti e caricati i parametri di luminosità etc
		self._fileName = fileConfig
		self.realodConfig()
		logging.basicConfig(filename=self._logPath, level=logging.ERROR,
					format='%(asctime)s %(levelname)s %(name)s %(message)s')
		self._logger=logging.getLogger(__name__)
		self._picam2 = None
		self._lsize = (320, 240)
		self._recording = False
 
#funzioni per configurare la luminosità, la saturazione e la soglia e per riprendere i parametri della cam
	#setter soglia di segmentazione
	@property
	def thresh(self):
		return self._thresh
	

	@thresh.setter
	def thresh(self, new_value):
		if new_value == "default":
			self._thresh = 7
		else:
			self._thresh = int(new_value)
		self._saveConfig()

	def _saveConfig(self):
		config = {"threshold":7, "url": '', "logPath": None}
		config["threshold"] = self._thresh
		config["url"] = self._url
		config["logPath"] = self._logPath
		with open(self._fileName, "w") as outfile:
			json.dump(config, outfile)

	def realodConfig(self):
		with open(self._fileName, "r") as file:
			config = json.load(file)	
		self._thresh = config["threshold"]
		self._url = config["url"]
		self._logPath= config["logPath"] 


	def getConfig(self):
		config = {'threshold': self._thresh}
		return config

	def start(self):
		if not self._recording:
			self._recording = True
			self._record()
		return True

	def _record(self):	
		#configurazione sbagliata
		self._picam2 = Picamera2()
		video_config = self._picam2.create_video_configuration(main={"size": (1280, 720), "format": "RGB888"}, lores={"size": self._lsize, "format": "YUV420"}, transform=Transform(vflip=True))
		self._picam2.configure(video_config)
		self._encoder = H264Encoder(1000000)	
		self._picam2.start()
		w, h = self._lsize
		prev = None
		encoding = False
		ltime = 0
		try:
		#possibile funzione per mandare i video
			while self._recording:
				cur = self._picam2.capture_buffer("lores")
				cur = cur[:w * h].reshape(h, w)
				if prev is not None:
					# Measure pixels differences between current and
					# previous frame
					mse = np.square(np.subtract(cur, prev)).mean()
					#mse è la soglia
					if mse > self._thresh:
						if not encoding:
							##questo encoder secondo me è usabile come file da mandare
							self._encoder.output = FfmpegOutput("video/motion.mp4")
							self._picam2.start_encoder(self._encoder)
							encoding = True
						ltime = time.time()
					else:
						if encoding and time.time() - ltime > 2.0:
							##dipende com'è il file ma quando è stabile qua sarebbe da ritornare l'encoder
							self._picam2.stop_encoder()
							encoding = False
							files = {'media': open('video/motion.mp4', 'rb')}
							r = requests.post(self._url, files=files)
							##invia il file in bianco e nero
				prev = cur
		except Exception as e:
			self._logger.error(e)
			self._picam2.stop()
			self._picam2.close()
			self._recording = False
		self._picam2.stop()
		self._picam2.close()

	def stop(self):
		self._recording = False

	def pic(self):
		s = None
		try:
			##trova un modo per ritornare un file
			##occhio qui il metodo va diviso, se sono in recording devo prendere un frame altrimenti faccio al foto
			if self._recording:
				img = self._picam2.capture_image()
				gray_img = img.convert("L")
				s = gray_img
			else:
				self._picam2 = Picamera2()
				self._picam2.configure(self._picam2.create_still_configuration(main={"size": (1280, 720)},transform=Transform(vflip=True)))
				self._picam2.start()
				time.sleep(1)
				img = self._picam2.capture_image()
				gray_img = img.convert("L") 
				s = gray_img
				self._picam2.stop()
				self._picam2.close()
		except Exception as e:
			self._logger(e)
		return s


if __name__ == '__main__' :
	hasRun=True
	cam = spycam()
	while hasRun:
		print('Scegli il comando:\n 1 - Start\n 2 - Stop \n 3 - Foto \n 4 - Esci')
		deg = int(input())
		if deg == 1:
			t0 = threading.Thread(target = cam.start)
			t0.start()	
		elif deg == 2:
			cam.stop()
		elif deg == 3:
			cam.pic()
		elif deg == 4:
			cam.stop()
			hasRun = False
		elif deg == 5:
			print(cam.getConfig())
	print('Ciao ciao')
