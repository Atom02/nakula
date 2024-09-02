from fastapi import APIRouter, Request, Query, Body, Form
from pydantic import BaseModel, Field
from typing import Optional,Annotated
from rbac.AuthManagerRedis import AuthManagerRedis
from helper.rediscache import myCache

router = APIRouter(
	prefix="/v1/auth",
	tags=["v1-auth"],
    # include_in_schema=False,
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


class createRoleParams(BaseModel):
    name: str = Field(..., description="Role Name")

class createRoleResponse(BaseModel):
    status: bool = Field(False, description="Request Status", example=True)
    message: str = Field(None, description="Request Message", example="Role Created")

@router.post("/create-role", response_model=createRoleResponse, response_model_exclude_none = True)
async def createrole(request:Request, params:createRoleParams):
    db = request.app.state.db
    resp = createRoleResponse()
    try:
        cache = myCache()
        await cache.set("test5",0.2)
        await cache.set("test6",2)
        test_get = await cache.get("test2")
        test_get2 = await cache.get("test5")
        if test_get:
            print("BOOL IS READ")
        print("TEST GET",test_get, test_get2)
        auth = AuthManagerRedis(db)

        check_role = await auth.getRole(params.name)
        print("ROLE IS", check_role)
        if check_role is not None:
            raise ValueError(f"{params.name} already exists")

        role = await auth.createRole(params.name)
        role.description = "ADMIN ROLE"
        await auth.add(role)
        db.commit()

        resp.status = True
        resp.message = "Role Created"
    except Exception as e:
        resp.status = False
        resp.message = f"ERROR OCCURED {e}"
        # permissions = auth.createPermission("access")
    
    resp.status = True
    # resp.message = params.name
    return resp

class removeRoleParams(BaseModel):
    name: str = Field(..., description="Role Name")

class removeRoleResponse(BaseModel):
    status: bool = Field(False, description="Request Status", example=True)
    message: str = Field(None, description="Request Message", example="Role Created")

@router.post("/remove-role", response_model=removeRoleResponse, response_model_exclude_none = True)
async def remove_role(request:Request, params:removeRoleParams):
    db = request.app.state.db
    resp = removeRoleResponse()

    try:
        auth = AuthManagerRedis(db)
        role = await auth.getRole(params.name)
        if check_role is None:
            raise ValueError(f"{params.name} doesn't exists")
        
        await role.remove()
        db.commit()

        resp.status = True
        resp.message = "Role Removed"
    except Exception as e:
        resp.status = False
        resp.message = f"ERROR OCCURED {e}"

    resp.status = True
    return resp


class updateRoleParams(BaseModel):
    name: str = Field(..., description="Role Name", example="admin")
    permissions: list[str] = Field(..., description="List of permissions", example=["dashboard_access"])

class updateRoleResponse(BaseModel):
    status: bool = Field(False, description="Request Status", example=True)
    message: str = Field(None, description="Request Message", example="Role Created")

@router.post("/update-role", response_model=updateRoleResponse, response_model_exclude_none = True)
async def update_role(request:Request, params:updateRoleParams):
    db = request.app.state.db
    resp = removeRoleResponse()

    try:
        auth = AuthManagerRedis(db)
        role = await auth.getRole(params.name)
        if check_role is None:
            raise ValueError(f"{params.name} doesn't exists")
        
        await role.update()
        db.commit()

        resp.status = True
        resp.message = "Role Removed"
    except Exception as e:
        resp.status = False
        resp.message = f"ERROR OCCURED {e}"

    resp.status = True
    return resp

class permisionParams(BaseModel):
    name: str = Field(None, description="Permision Name", example="admin")

class permisionResponse(BaseModel):
    status: bool = Field(False, description="Request Status", example=True)
    permisions: list[dict] = Field(None, description="Permissions List", example=[{}])
    message: str = Field(None, description="Request Message", example="Role Created")

@router.get("/permisions", response_model=permisionResponse, response_model_exclude_none = True)
async def permisions(request:Request, name: str = Query(None, description="Permision Name", example="admin")):
    db = request.app.state.db
    resp = permisionResponse()

    try:
        auth = AuthManagerRedis(db)
        permission = None
        if name is None:
            permission = await auth.getPermissionsGrouped()
        else:
            permission = await auth.getPermission(name)
        
        print("perm",permission)
        resp.status = True
        resp.permisions = permission
    except Exception as e:
        resp.status = False
        resp.message = f"ERROR OCCURED {e}"

    resp.status = True
    return resp