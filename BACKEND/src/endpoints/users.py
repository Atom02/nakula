from fastapi import APIRouter, Request, Query
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(
	prefix="/v1/users",
	tags=["v1-users"],
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