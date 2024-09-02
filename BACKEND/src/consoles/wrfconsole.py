from fastapi import APIRouter, Request, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional
from .depends import check_ip
import os
import mariadb
import traceback
from pathlib import Path
from netCDF4 import Dataset, date2num,num2date
from constants import ROOTDIR,HDFDIR,WRFBUFFERDIR
from helper.hdf import hdf as hdfhelper
from helper.dasarian import dasarian as dasarianhelper
import numpy as np
import subprocess
import shutil
from datetime import datetime, timezone, timedelta
import math

router = APIRouter(
	prefix="/console/wrf",
	tags=["CONSOLE-WRF"],
	responses={
		404: {
		"description": "NOT FOUND",
		"content": {
			"application/json": {
				"example" : "NOT FOUND"
			}
		}},
		403: {
		"description": "DENIED",
		"content": {
			"application/json": {
				"example" : "Request Denied"
			}
		}}
	},
)


class LogResponse(BaseModel):
	status: bool = Field(True,description = "Status", example=True)
	# data: Optional[dict] = Field(None, description = "Data", example={})
	# current_dasarian:Optional[int] = Field(None, description="Current Dasarian", example=202004)
	message:Optional[str] = Field(None, description="Message", example="Some Message")

@router.get("/log", response_model=LogResponse, response_model_exclude_none = True)
def log(request:Request, ip: str = Depends(check_ip)):
	db = request.app.state.db;
	cur = db.get()
	ins = 0   
	status = True
	message = "-"
	try:
		wrfBuffer = WRFBUFFERDIR
		wrfBufferAbs = os.path.join(ROOTDIR, wrfBuffer)
		files = os.listdir(wrfBufferAbs)
		inserted=[]     
		print(files)
		for f in files:
			if f.endswith(".nc") == True:					
				try:
					fsize = os.stat(os.path.join(wrfBufferAbs,f)).st_size
					# print("found size",fsize)
					q=""" insert into log_raw_file value('WRF',DEFAULT,%(directory)s,%(file)s,DEFAULT,%(size)s) """
					qp = {'directory':wrfBuffer,'file':f,'size':fsize}
					# db.cursor.execute(q,qp)
					cur.execute(q,qp)
					# print(cur._last_executed)
					ins+=1
				except Exception as exp:
					print(cur._paramlist)
					traceback.print_exc()
					continue
		db.commit()
	except mariadb.Error as e:
		status = False
		message = str(e)
	except Exception as e:
		status = False
		message = str(e)
	
	return LogResponse(status=status, processed=ins, message=message)

class ProcessResponse(BaseModel):
	status: bool = Field(True,description = "Status", example=True)
	message:Optional[str] = Field(None, description="Message", example="Some Message")
@router.get("/process", response_model=ProcessResponse, response_model_exclude_none = True)
def process(request:Request, ip: str = Depends(check_ip)):
	status = True
	message = "-"
	#load file one order by date asc and processed = 0
	#proc the rain first
	#proc other data you want
	#create hdf to store the data
	#store the data\
	return ProcessResponse(status=status,  message=message)