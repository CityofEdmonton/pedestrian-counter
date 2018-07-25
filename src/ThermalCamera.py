from Adafruit_AMG88xx import Adafruit_AMG88xx
from ThermalData import ThermalData


class ThermalCamera(ThermalData):
	def __init__(self):
		MINTEMP = 26
		MAXTEMP = 32
		

	def testFunction(self):
		print("test")
