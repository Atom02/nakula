# import h5py as h5
# import os
# from pathlib import Path
import numpy as np
class pointToMatrix:    
	def __init__(self):
		pass
	@staticmethod
	def find_nearest(array, value):
		array = np.asarray(array)
		idx = (np.abs(array - value)).argmin()
		return {"key":idx,"v":array[idx]}