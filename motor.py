#!/usr/bin/env python 
# -*- coding: utf-8 -*-

# libraries
import time
import RPi.GPIO as GPIO
import json
import math

class MotorStep(object):
        """docstring for MotorStep"""
        def __init__(self, pinsList, fileConfig):
                # Use BCM GPIO references
                # Instead of physical pin numbers
                self._fileName = fileConfig
                GPIO.setmode(GPIO.BCM)
                # Define GPIO signals to use Pins 18,22,24,26 GPIO24,GPIO25,GPIO8,GPIO7
                self._StepPins = pinsList
                # Set all pins as output
                for pin in self._StepPins:
                        GPIO.setup(pin,GPIO.OUT)
                        GPIO.output(pin, False)
                # Define some settings
                self.WaitTime = 0.005

                # Define simple sequence
                StepCount1 = 4
                Seq1 = []
                Seq1 = [i for i in range(0, StepCount1)]
                Seq1[0] = [1,0,0,0]
                Seq1[1] = [0,1,0,0]
                Seq1[2] = [0,0,1,0]
                Seq1[3] = [0,0,0,1]
                # Define advanced half-step sequence
                StepCount2 = 8
                Seq2 = []
                Seq2 = [i for i in range(0, StepCount2)]
                Seq2[0] = [1,0,0,0]
                Seq2[1] = [1,1,0,0]
                Seq2[2] = [0,1,0,0]
                Seq2[3] = [0,1,1,0]
                Seq2[4] = [0,0,1,0]
                Seq2[5] = [0,0,1,1]
                Seq2[6] = [0,0,0,1]
                Seq2[7] = [1,0,0,1]
                # Choose a sequence to use
                self._Seq = Seq1
                self._StepCount = StepCount1

                #try to open the configuration file, then go to the zero
                try:
                        f = open(self._fileName)
                        config = json.load(f)
                        self._zeroDeg = int(config["zeroDeg"])
                        self._e = float(config['errors'])
                        self._limitRight = config['limitRight']
                        self._limitLeft = config['limitLeft']
                        f.close()
                        self.ToZero()

                except:
                        self._zeroDeg = 0 #number of step to zero deg
                        self._e = 0
                        self._limitRight = None
                        self._limitLeft = None
                        self._SaveConfig()


        def _StepsHandle(self, deg):
                self._e = self._e + round((1024/360)*deg) - (1024/360)*deg
                nb = int(round((1024/360)*deg))
                self._SaveConfig()
                return nb

        def _SaveConfig(self):
                config = {"zeroDeg":0, "errors": 0, "limitLeft": None, "limitRight": None}
                config["zeroDeg"] = self._zeroDeg
                config["errors"] = self._e
                config["limitRight"] = self._limitRight
                config["limitLeft"] =  self._limitLeft
                with open(self._fileName, "w") as outfile:
                    json.dump(config, outfile)

        def _FixErorrs(self):
                fixStep = 0
                margin = round(self._e) - self._e
                if abs(margin) <= 0.2 and round(self._e) != 0:
                        fixStep = int(round(self._e))
                        self._e = 0
                        self._SaveConfig()
                return fixStep 

        #check if right or left are null or int, else don't update values
        def SetLimits(self, right, left):
                status = True
                if type(right) == int and type(left) == int:
                        right = int(right)
                        left = int(left)
                        if right <= 0:
                                right = 1
                        if right > 180:
                                right = 180
                        if left >= 0:
                                left = -1
                        if left < -180:
                                left = -180
                        self._limitRight = right
                        self._limitLeft = left
                        self._SaveConfig()
                else:
                        status = False
                return status

        def SetRightLimit(self, right):
                status = True
                if type(right) == int and self._limitLeft != None and self._limitLeft != -360:
                        right = int(right)
                        if right <= 0:
                                right = 1
                        if right > 180:
                                right = 180
                        self._limitRight = right
                        self._SaveConfig()
                else:
                        status = False
                return status

        def SetLeftLimit(self, left):
                status = True
                if type(left) == int and self._limitRight != None and self._limitRight != 360:
                        left = int(left)
                        if left >= 0:
                                left = - 1
                        if left < -180:
                                left = - 180
                        self._limitLeft = left
                        self._SaveConfig()
                else:
                        status = False
                return status

        def GetLimits(self):
                limits = {"right": self._limitRight, "left": self._limitLeft}
                return limits

        def DelLimits(self):
                self._limitRight = 360
                self._limitLeft = -360
                self._SaveConfig()
                return True

        def Rotation(self, degIn):
                #occhio al no limiti
                deg360 = degIn - (math.floor(degIn/360)*360) 
                if deg360 > 180:
                        path = deg360 - 360 
                        pathsx = path
                        pathdx = deg360
                else:
                        path = deg360
                        pathsx = deg360 - 360
                        pathdx = path
                #qui differenzio in base al limite
                if self._limitLeft != -360 and self._limitRight != 360:
                        x1s = pathsx + self._zeroDeg
                        x1d = pathdx + self._zeroDeg
                        dsx = abs(self._limitLeft) - abs(x1s)
                        ddx = abs(self._limitRight) - abs(x1d)
                        x1 = path ##punto presunto finale
                        if dsx < 0 and ddx < 0:
                                x1 = self._limitLeft if dsx > ddx else self._limitRight
                        elif dsx >0  or  ddx > 0:
                                x1 = x1s if dsx > ddx else x1d
                        path = x1 - self._zeroDeg
                self._Steps(path)
                self._zeroDeg = x1
                zero360 = self._zeroDeg - (math.floor(self._zeroDeg/360)*360)
                self._zeroDeg = zero360 - 360 if zero360 > 180 else zero360
                self._SaveConfig()
                return path

        def _Steps(self, deg):
                nb = self._StepsHandle(deg)
                nb = nb + self._FixErorrs()
                StepCounter = 0
                if nb<0: sign=-1
                else: sign=1
                nb=sign*nb*2 #times 2 because half-step
                for i in range(nb):
                        for pin in range(4):
                                xpin = self._StepPins[pin]
                                if self._Seq[StepCounter][pin]!=0:
                                        GPIO.output(xpin, True)
                                else:
                                        GPIO.output(xpin, False)
                        StepCounter += sign
                        if (StepCounter==self._StepCount):
                                StepCounter = 0
                        if (StepCounter<0):
                                StepCounter = self._StepCount-1
                        # Wait before moving on
                        time.sleep(self.WaitTime)


        def ToZero(self):
                zero = - self._zeroDeg
                self._Steps(zero)
                self._zeroDeg = 0
                #self._e = 0 a questo punto è sbagliato perché torno più o meno a zero
                self._SaveConfig()

        def SetZero(self):
                self._zeroDeg = 0
                self._e = 0
                self._SaveConfig()

        def StopMotor(self):
                for pin in self._StepPins:
                        GPIO.output(pin, False)

        def GetDeg(self):
                return self._zeroDeg


        # Start main loop
        nbStepsPerRev=2048

if __name__ == '__main__' :
    hasRun=True
    motor = MotorStep([24,25,8,7])
    while hasRun:
            #steps(nbStepsPerRev)# parcourt un tour dans le sens horaire
            #time.sleep(1)
            #steps(-nbStepsPerRev)# parcourt un tour dans le sens anti-horaire
            #time.sleep(1)
            print('Scegli i gradi da fare')
            deg = int(input())
            #nbStepsPerRev = int((1024/360)*deg)
            motor.Rotate(deg)
            ptr = 'Sei a ' + str(motor.GetDeg()) + '° dallo zero'
            print(ptr)
            print('Vuoi continuare?')

            hasRun=eval(input())
    motor.ToZero()

    print("Stop motor")
    motor.StopMotor()