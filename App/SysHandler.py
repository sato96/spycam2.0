import platform
import socket
import psutil
import uuid
import regex as re
import time
import os
class SystemHandler:

	@staticmethod
	def getSystemInfo():
		try:
			info={}
			info['platform']=platform.system()
			info['platform-release']=platform.release()
			info['platform-version']=platform.version()
			info['hostname']=socket.gethostname()
			info['ip-address']=SystemHandler.get_local_ip()
			info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
			info['processor']=platform.processor()
			info['ram']=str(round(psutil.virtual_memory().total / (1024.0 **3),3))+" GB"
			info['ram-available'] = str(round(psutil.virtual_memory().available / (1024.0 ** 3),3)) + " GB"
			return info
		except Exception as e:
			pass
	@staticmethod
	def get_local_ip():
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		try:
			# doesn't even have to be reachable
			s.connect(('192.255.255.255', 1))
			IP = s.getsockname()[0]
		except:
			IP = '127.0.0.1'
		finally:
			s.close()
		return IP

	@staticmethod
	def reboot():
		time.sleep(180)
		os.system('systemctl reboot -i')
