import h5py as h5
import os
from pathlib import Path
import numpy as np
import traceback
class hdf:
	f = None
	def __init__(self):
		pass
	
	@staticmethod
	def create(fileTarget):
		if os.path.isfile(fileTarget):
			raise IOError("ERROR "+fileTarget+"File Exist")
		fhdf = h5.File(fileTarget,"x")
		fhdf.close()

	@staticmethod
	def read(fileTarget = None, readOnly = True):
		if not os.path.isfile(fileTarget):
			return None
		else:
			if readOnly:
				# print("open In Read ONly")
				mode = "r"
			else:
				mode = "r+"
			try:
				return h5.File(fileTarget,mode)
			except Exception as e:
				traceback.print_exc()
				return None
	
	# def createGroup(self,groupName):
	# 	self.f.create_group(groupName)

	# def gethdfObj(self):
	# 	return self.f

	# def close(self):
	# 	self.f.close()
	
	# def find_nearest(self,array, value):
	# 	array = np.asarray(array)
	# 	idx = (np.abs(array - value)).argmin()
	# 	# idx2 = (np.abs(array - value)).argmax()
	# 	# print(value,array[idx],idx)
	# 	return {"key":idx,"v":array[idx]}