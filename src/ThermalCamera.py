from Adafruit_AMG88xx import Adafruit_AMG88xx
from ThermalData import ThermalData
import numpy as np


class ThermalCamera(ThermalData):
	def __init__(self, saveToDisk = False, saveLocation = "./"):
		self.MINTEMP = 26
		self.MAXTEMP = 32
		#how many color values we can have
		self.COLORDEPTH = 1024
		self.sensor = Adafruit_AMG88xx()
		self.saveToDisk = saveToDisk
		self.saveLocation = saveLocation
		self.numberOfFrames = 0
		self.frames = []


	def get(self):
		pixels = self.sensor.readPixels()
		pixels = [self.map(p, self.MINTEMP, self.MAXTEMP, 0, self.COLORDEPTH - 1) for p in pixels]
		if self.saveToDisk:
			self.frames.append(pixels)
			return self.frames[-1]
		else:
			return pixels

	def save(self):
		if self.saveToDisk:
			print("Writing to disk")
			np.savetxt(self.saveLocation, self.frames)
		else:
			return
