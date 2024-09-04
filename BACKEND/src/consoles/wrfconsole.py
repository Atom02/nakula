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
	processed:Optional[int] = Field(None, description="Processed", example=0)

@router.get("/log", response_model=LogResponse, response_model_exclude_none = True)
def log(request:Request, forcerelog: bool = Query(False, description="Force relog of all files"), ip: str = Depends(check_ip)):
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
				except mariadb.IntegrityError as e:
					if "Duplicate entry" in str(e):  # Check if the error is a duplication error
						print(f"Duplicate entry for wrf {qp}. Skipping...")
						if forcerelog == True:
							q=""" update log_raw_file set processed = 0, size = %(size)s where name = 'WRF' and relativedir = %(relativedir)s and file = %(file)s """
							qp = {'size': fsize, 'relativedir':wrfBuffer,'file':f}
							print(q,qp)
							cur.execute(q,qp)
							ins+=1
						continue
					else:
						raise ValueError(str(e))
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
	finally:
		cur.close()
	
	return LogResponse(status=status, processed=ins, message=message)


class RepackResponse(BaseModel):
	status: bool = Field(True,description = "Status", example=True)
	message:Optional[str] = Field(None, description="Message", example="Some Message")
@router.get("/repack", response_model=RepackResponse, response_model_exclude_none = True)
def repack(request:Request, ip: str = Depends(check_ip)):
	status = True
	message = "-"
	db = request.app.state.db;
	cur = db.get()
	try:
		q=""" select * from hdf_files where hdf_id='wrf' and status=1 limit 1 """
		cur.execute(q)
		res = cur.fetchone()
		if res is not None:
			current_time = datetime.utcnow()
			formatted_time = current_time.strftime("%Y%m%d%H%M")
			res['hdf_path_full']=os.path.join(ROOTDIR, res['hdf_path'])
			file = os.path.join(res['hdf_path_full'],res['hdf_file'])
			repack = os.path.join(ROOTDIR,HDFDIR,"wrf_"+formatted_time+".hdf")

			if os.path.isfile(file):
				print("REPACKING WRF HDF")
				repackProcess = subprocess.run(["h5repack",file,repack],timeout=60*10, check=True)
				print("REPACK DONE")
				if(os.path.isfile(repack)):
					q=""" update hdf_files set status = 0 """
					cur.execute(q)
					q=""" insert into hdf_files values ('wrf',%(path)s,%(file)s, 1, DEFAULT) """
					cur.execute(q,{
						"path":HDFDIR,
						"file":"wrf_"+formatted_time+".hdf"
					})
					db.commit()
	except Exception as e:
		status = False
		message = str(e)
	finally:
		cur.close()
	
	return RepackResponse(status = status, message = message)

class CleanResponse(BaseModel):
	status: bool = Field(True,description = "Status", example=True)
	message:Optional[str] = Field(None, description="Message", example="Some Message")
@router.get("/cleanup", response_model=CleanResponse, response_model_exclude_none = True)
def cleanup(request:Request, ip:str = Depends(check_ip)):
	status = True
	message = "-"

	db = request.app.state.db;
	cur = db.get()

	q=""" select * from hdf_files where hdf_id = 'wrf' and status = 0 order by created_on asc limit 2 """
	cur.execute(q)
	res = cur.fetchall()
	if res:
		for item in res:
			hdf_full_path = os.path.join(ROOTDIR, item['hdf_path'], item['hdf_file'])
			if(os.path.isfile(hdf_full_path)):
				os.remove(hdf_full_path)
			else:
				q=""" delete from hdf_files where hdf_id = 'wrf' and hdf_file=%(file)s and hdf_path=%(path)s and status = 0 """
				qp={
					'file':item['hdf_file'],
					'path':item['hdf_path']
				}
				cur.execute(q,qp)
				db.commit()

	return CleanResponse(status = True, message=message)
	


class ProcessResponse(BaseModel):
	status: bool = Field(True,description = "Status", example=True)
	message:Optional[str] = Field(None, description="Message", example="Some Message")
@router.get("/process", response_model=ProcessResponse, response_model_exclude_none = True)
def process(request:Request, ip: str = Depends(check_ip)):
	db = request.app.state.db;
	cur = db.get()
	status = True
	message = "-"
	hdf_object = None
	try:
		
		#load file one order by date asc and processed = 0
		q = """ select * from log_raw_file where processed = 0 order by insertedtime asc limit 4 """
		cur.execute(q)
		nc_files = cur.fetchall()
		print("nc_files",nc_files)
		if not nc_files:
			raise ValueError("No files to process")
		
		hdf_dir = os.path.join(ROOTDIR,HDFDIR)
		q=""" select * from hdf_dictionary where hdf_id = 'wrf' limit 1"""
		cur.execute(q)
		hdf_dictionary = cur.fetchone()
		if hdf_dictionary is None:
			q=""" insert into hdf_dictionary values ('wrf','WRF hdf','HDF data for FILE STORAGE') """
			cur.execute(q)
			db.commit()
		
		hdf_file_name = 'wrf.hdf'
		hdf_file = os.path.join(hdf_dir,hdf_file_name)
		q=""" select * from hdf_files where hdf_id = 'wrf' and status = 1 limit 1 """
		cur.execute(q)
		hdf_file = cur.fetchone()
		if hdf_file is None:
			q=""" insert into hdf_files values ('wrf',%(path)s,%(filename)s,%(status)s, DEFAULT) """
			qp = {
				"path":hdf_dir,
				"filename":HDFDIR,
				"status":1
			}
			cur.execute(q,qp)
			db.commit()
		else:
			hdf_file_name = hdf_file['hdf_file']
			hdf_file = os.path.join(hdf_dir,hdf_file_name)
		
		print("USING HDF", hdf_file)
		
		q=""" select * from hdf_data_dictionary where hdf_id = 'wrf' """
		cur.execute(q)
		hdf_data_dictionary = cur.fetchall()
		print("DATA DICTIONARY",hdf_data_dictionary)
		if not hdf_data_dictionary:
			print("INSERT DATA DICTIONARY")
			q=""" insert into hdf_data_dictionary values ('wrf','wrf_precipitaion','Rain','Rain Precipitaion') """
			cur.execute(q)
			q=""" insert into hdf_data_dictionary values ('wrf','wrf_temp','Temperature','Temperature') """
			cur.execute(q)
			q=""" insert into hdf_data_dictionary values ('wrf','wrf_humidity','Humidity','Humidity') """
			cur.execute(q)
			q=""" insert into hdf_data_dictionary values ('wrf','wrf_psfc','Surface Pressure','Surface Pressure') """
			cur.execute(q)
			q=""" insert into hdf_data_dictionary values ('wrf','wrf_olr','Outgoing Longwave Radiation','Outgoing Longwave Radiation') """
			cur.execute(q)
			q=""" insert into hdf_data_dictionary values ('wrf','wrf_sst','Sea Surface Temperature','Sea Surface Temperature') """
			cur.execute(q)
			q=""" insert into hdf_data_dictionary values ('wrf','wrf_u10','U at 10m','U at 10m') """
			cur.execute(q)
			q=""" insert into hdf_data_dictionary values ('wrf','wrf_v10','V at 10m','V at 10m') """
			cur.execute(q)
			db.commit()

		try:
			if not os.path.exists(hdf_dir):
				Path(hdf_dir).mkdir(parents=True, exist_ok=True)
			if not os.path.isfile(hdf_file):
				hdfhelper.create(hdf_file)
		except Exception as e:
			raise ValueError(str(e))
		
		hdf_object = hdfhelper.read(hdf_file, readOnly=False)
		
		for nc_file in nc_files:	
			time_loop = 0
			file = os.path.join(ROOTDIR,nc_file['relativedir'],nc_file['file'])
			print("file",file)
			nc = Dataset(file)
			time = nc.variables['XTIME']
			timeUnit = time.units
			times = time[:]
			dtime = []

			rainc = nc.variables['RAINC'][:]
			rainnc = nc.variables['RAINNC'][:]
			var_temp = nc.variables['T2'][:]
			var_humidity = nc.variables['Q2'][:]
			var_surface_pressure = nc.variables['PSFC'][:]
			var_olr = nc.variables['OLR'][:]
			var_sst = nc.variables['SST'][:]
			var_u10 = nc.variables['U10'][:]
			var_v10 = nc.variables['V10'][:]

			if 'lon' not in hdf_object:
				lon = nc.variables['XLONG'][:]
				hdf_object.create_dataset('lon', data=lon[0,:])
				hdf_object["lon"].attrs["long_name"]="Longitude"
				hdf_object["lon"].attrs["standard_name"]="longitude"
				hdf_object["lon"].attrs["units"]="degrees_east"
				hdf_object["lon"].attrs["axis"]="X"
			
			if 'lat' not in hdf_object:
				lat = nc.variables['XLAT'][:]
				hdf_object.create_dataset('lat', data=lat[:,0])
				hdf_object["lat"].attrs["long_name"]="Latitude"
				hdf_object["lat"].attrs["standard_name"]="latiude"
				hdf_object["lat"].attrs["units"]="degrees_north"
				hdf_object["lat"].attrs["axis"]="Y"
			
			if "terrain" not in hdf_object:
				terrain = nc.variables['HGT'][:]
				hdf_object.create_dataset('terrain', data=terrain)
				hdf_object['terrain'].attrs['long_name']='Terrain Height'
				hdf_object['terrain'].attrs['standard_name']='Terrain Height'
				hdf_object['terrain'].attrs['units']='m'
				hdf_object['terrain'].attrs['description']='Terrain Height'

			if 'precip' not in hdf_object:
				hdf_object.create_group('precip')
				hdf_object['precip'].attrs['long_name']='Precipitation'
				hdf_object["precip"].attrs["standard_name"]="Precipitation"
				hdf_object['precip'].attrs['units']='mm/hour'
			
			if 'temp' not in hdf_object:
				hdf_object.create_group('temp')
				hdf_object['temp'].attrs['long_name']='Temperature'
				hdf_object['temp'].attrs['standard_name']='Temperature'
				hdf_object['temp'].attrs['units']='Celsius'
				hdf_object['temp'].attrs['description']='Temperature at 2m'
			
			if 'humidity' not in hdf_object:
				hdf_object.create_group('humidity')
				hdf_object['temp'].attrs['long_name']='Humidity'
				hdf_object['temp'].attrs['standard_name']='Humidity'
				hdf_object['temp'].attrs['units']='kg/kg'
				hdf_object['temp'].attrs['description']='Humidity at 2m'
			
			if "PSFC" not in hdf_object:
				hdf_object.create_group('PSFC')
				hdf_object['PSFC'].attrs['long_name']='Surface Pressure'
				hdf_object['PSFC'].attrs['standard_name']='Surface Pressure'
				hdf_object['PSFC'].attrs['units']='Pa'
				hdf_object['PSFC'].attrs['description']='Surface Pressure'
			
			if "OLR" not in hdf_object:
				hdf_object.create_group('OLR')
				hdf_object['OLR'].attrs['long_name']='Outgoing Longwave Radiation'
				hdf_object['OLR'].attrs['standard_name']='Outgoing Longwave Radiation'
				hdf_object['OLR'].attrs['units']='W/m2'
				hdf_object['OLR'].attrs['description']='Outgoing Longwave Radiation'
			
			if "SST" not in hdf_object:
				hdf_object.create_group('SST')
				hdf_object['SST'].attrs['long_name']='Sea Surface Temperature'
				hdf_object['SST'].attrs['standard_name']='Sea Surface Temperature'
				hdf_object['SST'].attrs['units']='Celsius'
				hdf_object['SST'].attrs['description']='Sea Surface Temperature'
			
			if "U10" not in hdf_object:
				hdf_object.create_group('U10')
				hdf_object['U10'].attrs['long_name']='U at 10m'
				hdf_object['U10'].attrs['standard_name']='U at 10m'
				hdf_object['U10'].attrs['units']='m/s'
				hdf_object['U10'].attrs['description']='U at 10m'

			if "V10" not in hdf_object:
				hdf_object.create_group('V10')	
				hdf_object['V10'].attrs['long_name']='V at 10m'
				hdf_object['V10'].attrs['standard_name']='V at 10m'
				hdf_object['V10'].attrs['units']='m/s'
				hdf_object['V10'].attrs['description']='V at 10m'

			hdf_object_precip = hdf_object['precip']
			hdf_object_temp = hdf_object['temp']
			hdf_object_humidity = hdf_object['humidity']
			hdf_object_psfc = hdf_object['PSFC']
			hdf_object_olr = hdf_object['OLR']
			hdf_object_sst = hdf_object['SST']
			hdf_object_u10 = hdf_object['U10']
			hdf_object_v10 = hdf_object['V10']
			# if 'landmask' not in hdf_object:
			# 	lmask = nc.variables['LANDMASK'][:]
			# 	hdf_object.create_dataset('landmask',data=lmask)
			# 	hdf_object['landmask'].attrs['long_name']='Land Cover'
			# 	hdf_object['landmask'].attrs['description']='Land Cover'

			for t in times:
				dtime.append(num2date(t,timeUnit))
			
			res_paths = []
			for i,d in enumerate(dtime):
				key = d.strftime("%Y-%m-%d %H:00:00")
				dbkey = d.strftime("%Y-%m-%d %H:00:00")
				try:
					crainc = rainc[i][:]
					crainnc = rainnc[i][:]
					nrainc = rainc[i+1][:]
					nrainnc = rainnc[i+1][:]
					# rain(t) = (rainc (t+1) + rainnc (t+1) ) - (rainc(t)+rainnc(t))
					current_rain = (nrainc + nrainnc) - (crainc + crainnc)
					if key in hdf_object_precip:
						compare_rain = current_rain == hdf_object_precip[key]
						is_equal = compare_rain.all()
						if is_equal == True:
							del hdf_object_precip[key]
					
					hdf_object_precip.create_dataset(key, data=current_rain)
					hdf_object_precip[key].attrs['time']=key
					hdf_object_precip[key].attrs['units']='mm/hour'
					hdf_object_precip[key].attrs['description']='Precipitation'
					res_paths.append({
						"path":"/".join(['precip',key]),
						"data_name":"wrf_precipitaion",
						"time":dbkey
					})
				except Exception as e:
					pass
				
				#======================= celcius temp =======================
				celsius_data = var_temp[i][:] - 273.15
				if key in hdf_object_temp:
					compare_temp = celsius_data == hdf_object_temp[key]
					is_equal = compare_temp.all()
					if is_equal == True:
						del hdf_object_temp[key]
				
				hdf_object_temp.create_dataset(key, data=celsius_data)
				hdf_object_temp[key].attrs['time']=key
				hdf_object_temp[key].attrs['units']='Celsius'
				hdf_object_temp[key].attrs['description']='Temperature'
				res_paths.append({
					"path":"/".join(['temp',key]),
					"data_name":"wrf_temp",
					"time":dbkey
				})

				#======================= surface temp =======================
				surface_celcius_data = var_sst[i][:] - 273.15
				if key in hdf_object_sst:
					compare_sst = surface_celcius_data == hdf_object_sst[key]
					is_equal = compare_sst.all()
					if is_equal == True:
						del hdf_object_sst[key]
				
				hdf_object_sst.create_dataset(key, data=surface_celcius_data)
				hdf_object_sst[key].attrs['time']=key
				hdf_object_sst[key].attrs['units']='Celsius'
				hdf_object_sst[key].attrs['description']='Sea Surface Temperature'
				res_paths.append({
					"path":"/".join(['SST',key]),
					"data_name":"wrf_sst",
					"time":dbkey
				})

				#======================= humidity =======================
				humidity_data = var_humidity[i][:]
				if key in hdf_object_humidity:
					compare_humidity = humidity_data == hdf_object_humidity[key]
					is_equal = compare_humidity.all()
					if is_equal == True:
						del hdf_object_humidity[key]
				
				hdf_object_humidity.create_dataset(key, data=humidity_data)
				hdf_object_humidity[key].attrs['time']=key,
				hdf_object_humidity[key].attrs['units']='kg/kg'
				hdf_object_humidity[key].attrs['description']='Humidity'
				res_paths.append({
					"path":"/".join(['humidity',key]),
					"data_name":"wrf_humidity",
					"time":dbkey
				})

				#======================= surface pressure =======================
				surface_pressure_data = var_surface_pressure[i][:]
				if key in hdf_object_psfc:
					compare_surface_pressure = surface_pressure_data == hdf_object_psfc[key]
					is_equal = compare_surface_pressure.all()
					if is_equal == True:
						del hdf_object_psfc[key]
				
				hdf_object_psfc.create_dataset(key, data=surface_pressure_data)
				hdf_object_psfc[key].attrs['time']=key
				hdf_object_psfc[key].attrs['units']='Pa'
				hdf_object_psfc[key].attrs['description']='Surface Pressure'
				res_paths.append({
					"path":"/".join(['PSFC',key]),
					"data_name":"wrf_psfc",
					"time":dbkey
				})

				#======================= outgoing longwave radiation =======================
				olr_data = var_olr[i][:]
				if key in hdf_object_olr:
					compare_olr = olr_data == hdf_object_olr[key]
					is_equal = compare_olr.all()
					if is_equal == True:
						del hdf_object_olr[key]
				
				hdf_object_olr.create_dataset(key, data=olr_data)
				hdf_object_olr[key].attrs['time']=key
				hdf_object_olr[key].attrs['units']='W/m2'
				hdf_object_olr[key].attrs['description']='Outgoing Longwave Radiation'
				res_paths.append({
					"path":"/".join(['OLR',key]),
					"data_name":"wrf_olr",
					"time":dbkey
				})

				#======================= u10 =======================
				u10_data = var_u10[i][:]
				if key in hdf_object_u10:
					compare_u10 = u10_data == hdf_object_u10[key]
					is_equal = compare_u10.all()
					if is_equal == True:
						del hdf_object_u10[key]
				
				hdf_object_u10.create_dataset(key, data=u10_data)	
				hdf_object_u10[key].attrs['time']=key
				hdf_object_u10[key].attrs['units']='m/s'
				hdf_object_u10[key].attrs['description']='U at 10m'
				res_paths.append({
					"path":"/".join(['U10',key]),
					"data_name":"wrf_u10",
					"time":dbkey
				})

				#======================= v10 =======================
				v10_data = var_v10[i][:]
				if key in hdf_object_v10:
					compare_v10 = v10_data == hdf_object_v10[key]
					is_equal = compare_v10.all()
					if is_equal == True:
						del hdf_object_v10[key]

				hdf_object_v10.create_dataset(key, data=v10_data)
				hdf_object_v10[key].attrs['time']=key
				hdf_object_v10[key].attrs['units']='m/s'
				hdf_object_v10[key].attrs['description']='V at 10m'
				res_paths.append({
					"path":"/".join(['V10',key]),
					"data_name":"wrf_v10",
					"time":dbkey
				})
			
			# print("res_paths",res_paths)
			for item in res_paths:
				# print("inserting", item)
				try:
					q=""" insert into hdf_data values (%(data_name)s, %(path)s,%(time)s) """
					qp = {
						"path":item['path'],
						"data_name":item['data_name'],
						"time":item['time']
					}
					cur.execute(q,qp)
				except mariadb.IntegrityError as e:
					if "Duplicate entry" in str(e):  # Check if the error is a duplication error
						# print(f"Duplicate entry for wrf {q}. Skipping...")
						continue
					else:
						raise ValueError(str(e))
			q=""" update log_raw_file set processed = 1 where name = %(name)s and relativedir = %(relativedir)s and file=%(file)s """
			qp={
				"name":nc_file['name'],
				"relativedir":nc_file['relativedir'],
				"file":nc_file["file"]
			}
			cur.execute(q,qp)
		db.commit()
	except Exception as e:
		status = False
		message = str(e)
		db.rollback()
	finally:
		if hdf_object is not None:
			hdf_object.close()
		cur.close()
	return ProcessResponse(status=status,  message=message)