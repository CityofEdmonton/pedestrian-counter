from Adafruit_AMG88xx import Adafruit_AMG88xx
from scipy import stats
import pickle


class ThermalCamera():
	def __init__(self):
		self.MINTEMP = 26
		self.MAXTEMP = 29
		#how many color values we can have
		self.COLORDEPTH = 1024
		self.sensor = Adafruit_AMG88xx()


	def get(self):
		pixels = self.sensor.readPixels()
#		print(pixels)
		mode_result = stats.mode([round(p) for p in pixels])
		if self.MAXTEMP <= mode_result[0]:
			self.MAXTEMP = 37
		pixels = [self.map_value(p, mode_result[0]+2, self.MAXTEMP, 0, self.COLORDEPTH - 1) for p in pixels]
		return pixels

	def map_value(self, x, in_min, in_max, out_min, out_max):
 		 return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

