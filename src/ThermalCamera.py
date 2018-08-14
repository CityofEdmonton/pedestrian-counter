from Adafruit_AMG88xx import Adafruit_AMG88xx
from ThermalData import ThermalData
from scipy import stats
import pickle


class ThermalCamera(ThermalData):
	def __init__(self, saveToDisk = False, saveLocation = "./"):
		self.MINTEMP = 26
		self.MAXTEMP = 29
		#how many color values we can have
		self.COLORDEPTH = 1024
		self.sensor = Adafruit_AMG88xx()
		self.saveToDisk = saveToDisk
		self.saveLocation = saveLocation
		self.numberOfFrames = 0
		self.frames = []


	def get(self):
		pixels = self.sensor.readPixels()
#		print(pixels)
		mode_result = stats.mode([round(p) for p in pixels])
		if self.MAXTEMP <= mode_result[0]:
			self.MAXTEMP = 37
		pixels = [self.map(p, mode_result[0]+2, self.MAXTEMP, 0, self.COLORDEPTH - 1) for p in pixels]
		if self.saveToDisk:
			self.frames.append(pixels)
			return self.frames[-1]
		else:
			return pixels

	def save(self):
		if self.saveToDisk:
			print("Writing to disk")
			outfile = open(self.saveLocation, "wb")
			pickle.dump(self.frames, outfile)
			outfile.close()
		else:
			return
