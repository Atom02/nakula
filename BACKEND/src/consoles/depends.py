from fastapi import Request, HTTPException
async def check_ip(request: Request):
    client_ip = request.client.host
    if client_ip != "127.0.0.1":
        raise HTTPException(status_code=403, detail="Access forbidden. IP is not from localhost.")
    return client_ip
    