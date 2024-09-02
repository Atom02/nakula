import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from routes.api import router as api_router
from fastapi.staticfiles import StaticFiles
from constants import ROOTDIR, HDFDIR
from helper.db import MyDb
# from helper.cache import cache
from fastapi_utils.tasks import repeat_every
from contextlib import asynccontextmanager
from dotenv import load_dotenv, find_dotenv
import os

# cache = TTLCache(maxsize=500, ttl=300)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("START")
    app.state.db = MyDb()
    yield
    print("SHUTDOWN")
    app.state.db.close()

env_file_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prod.env')

load_dotenv(env_file_path)

print("CACHE",os.getenv("CACHE"))

app = FastAPI(
    title="NAKULA API V.1",
    description="NAKULA API ENDPOINTS",
    version="1.0.0",
    root_path=os.getenv("MAIN_ROOTPATH","/"),
    docs_url=os.getenv("MAIN_DOCURL",None), 
    redoc_url=os.getenv("MAIN_REDOCURL",None),
    lifespan=lifespan
)
app.mount("/static",StaticFiles(directory="static"), name="static")
app.mount("/assets",StaticFiles(directory="assets"), name="assets")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == '__main__':
    print("running",ROOTDIR, HDFDIR)
    # uvicorn.run("main:app", host='0.0.0.0', port=8005, reload=True)
