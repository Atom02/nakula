from datetime import datetime, timedelta
import calendar

import math
class dasarian():
	def __init__(self):
		pass
	@staticmethod
	def dasarianInMonth(date):
		dasarian = 0
		d = int(date)
		if d <= 10:
			dasarian = 1
		elif d <= 20:
			dasarian = 2
		else:
			dasarian = 3
		return dasarian
	
	@staticmethod
	def getStartEndDate(year=None,dasarian=None,returnObj=False):
		if year is None or dasarian is None:
			raise ValueError('Year and Dasarian Number Must Be specified')
		
		month = math.floor(dasarian / 3)
		leftDasarian = dasarian - (month*3) 
		# print("LD",leftDasarian)

		rmonth = math.ceil(dasarian/3)
		if leftDasarian == 1:
			startDate = datetime.strptime(str(year)+"-"+str(rmonth)+"-01",'%Y-%m-%d')
			endDate = datetime.strptime(str(year)+"-"+str(rmonth)+"-10",'%Y-%m-%d')
		elif leftDasarian == 2:
			startDate = datetime.strptime(str(year)+"-"+str(rmonth)+"-11",'%Y-%m-%d')
			endDate = datetime.strptime(str(year)+"-"+str(rmonth)+"-20",'%Y-%m-%d')
		else:
			startDate = datetime.strptime(str(year)+"-"+str(rmonth)+"-21",'%Y-%m-%d')
			last_day_of_month = str(calendar.monthrange(year,rmonth)[1])
			endDate = datetime.strptime(str(year)+"-"+str(rmonth)+"-"+str(last_day_of_month),'%Y-%m-%d')
		delta = endDate - startDate 
		
		if returnObj:
			ret = {
				"startDate":startDate,
				"endDate":endDate
			}
			dateList = []
			for i in range(delta.days + 1):
				day = startDate + timedelta(days=i)
				dateList.append(day)
			ret['list'] = dateList
		else:
			ret = {
				"startDate":startDate.strftime("%Y-%m-%d"),
				"endDate":endDate.strftime("%Y-%m-%d")
			}
			dateList = []
			for i in range(delta.days + 1):
				day = startDate + timedelta(days=i)
				dateList.append(day.strftime("%Y-%m-%d"))
			ret['list'] = dateList
		
		return ret

	@staticmethod
	def getDasarianFromDate(date, withrange = False,  withObject = False):
		# print(type(date),isinstance(date,datetime))
		if isinstance(date,str):
			date = datetime.strptime(date,"%Y-%m-%d")
		month = date.month
		year = date.year
		day = date.day

		dasarianInMonth = dasarian.dasarianInMonth(day)
		currentDasarian = (month-1)*3 + dasarianInMonth
		ret = {'year':year,'dasarian':currentDasarian, 'month':month, 'inMonth':dasarianInMonth }
		if withrange:
			dasarianRange = dasarian.getStartEndDate(year,currentDasarian, withObject)
			ret.update(dasarianRange)
		return ret
		# range = getStartEndDate(year)
		# print(month,year,date,dasarianInMonth,currentDasarian)
	# def getDasarian(self,tahun,bulan):

	@staticmethod
	def getDasarianInYear(month,dasarian):
		if dasarian > 3 or dasarian < 1:
			raise ValueError("Invalid Dasarian")
		dasarianInYear = ((month-1)*3)+dasarian
		return dasarianInYear

	@staticmethod
	def getDasarianInMonth(dasarianName):
		dsnm = str(dasarianName)
		year = int(dsnm[0:4])
		dasarian = int(dsnm[-2:])
		dasarianInMonth = (dasarian % 3)        
		if dasarianInMonth == 0:
			dasarianInMonth = 3
		month = math.ceil(dasarian / 3)
		# print(year,dasarian,'inmonth',month, dasarianInMonth)
		# if month > 0 and dasarianInMonth == 0 :
		#     month = month - 1
		# dasarianInMonth = (dasarian - (month*3))
		return {"year":year,"dasarian":dasarian, "month":month, "inMonth":dasarianInMonth }

	@staticmethod
	def getNDasarian(year,dasarian,plus):
		dasarianToGet = dasarian+plus
		addYear = abs(dasarianToGet)//36
		if dasarianToGet > 36:
			yearToGet = year+addYear
			dasarianToGet = dasarianToGet % 36
			if dasarianToGet == 0:
				dasarianToGet = 36
		elif dasarianToGet < 1:
			yearToGet = year-(addYear+1)
			dasarianToGet = dasarianToGet % 36
			dasarianToGet = 36 - dasarianToGet
		else:
			yearToGet = year
		# ,"addYear":addYear, "dasarianPlus":dasarian+plus
		return {"year":yearToGet,"dasarian":dasarianToGet}