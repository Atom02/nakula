from fastapi import APIRouter
from src.endpoints import wrf,users,auth
from src.consoles import wrfconsole
router = APIRouter()
router.include_router(wrf.router)
# router.include_router(garam.router)
# router.include_router(ccam.router)

router.include_router(wrfconsole.router) 
router.include_router(users.router) 
router.include_router(auth.router)