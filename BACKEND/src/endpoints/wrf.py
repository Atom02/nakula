from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone, timedelta
from helper.dasarian import dasarian as dasarianhelper
from helper.hdf import hdf as hdfhelper
from helper.pointToMatrix import pointToMatrix
from constants import ROOTDIR,HDFDIR,WRFBUFFERDIR
import traceback
import os
import numpy as np
from helper.cache import cache
from pathlib import Path
from PIL import Image,ImageDraw
import cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mltcolors
import matplotlib.colorbar as mltcbar
import calendar

from enum import Enum

import io

router = APIRouter(
	prefix="/v1/wrf",
	tags=["v1-WRF"],
	responses={
		404: {
            "description": "NOT FOUND",
            "content": {
                "application/json": {
				    "example" : {"message":"NOT FOUND"}
			    }
		    }
        },
		403: {
            "description": "DENIED",
            "content": {
			    "application/json": {
				    "example" : {"message":"Request Denied"}
			    }
		    }
        }
	},
)

@router.get("/health")
async def health_check():
    return {"status": "ok"}