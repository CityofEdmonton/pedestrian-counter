class ThermalData():
	def get(self):
		raise NotImplementedError

	#some utility functions
	def constrain(self, val, min_val, max_val):
		return min(max_val, max(min_val, val))

	def map(self, x, in_min, in_max, out_min, out_max):
		return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
