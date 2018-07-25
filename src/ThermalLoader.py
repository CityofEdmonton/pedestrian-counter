from ThermalData import ThermalData
import pickle


class ThermalLoader(ThermalData):
	def __init__(self, saveToDisk = False, saveLocation = "./"):
		self.currentFrame = 0
		self.frames = []


	def get(self):
		self.currentFrame += 1
		return self.frames[self.currentFrame - 1]

	def load(self, file):
		infile = open(file,'rb')
		self.frames = pickle.load(infile)
		infile.close()
