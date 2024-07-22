from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import subprocess
import os
from typing import Optional

app = FastAPI()

security = HTTPBasic()

class InstallArgs(BaseModel):
    ipv4_address: Optional[str] = None
    public_ip: Optional[str] = None
    protocol: Optional[str] = 'udp'
    port: Optional[int] = 1194
    dns: Optional[int] = 1
    client_name: Optional[str] = 'client'

class Client(BaseModel):
    name: str

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == "admin" and credentials.password == "admin":
        return credentials.username
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

def run_script_with_args(args):
    try:
        result = subprocess.run(['sudo', 'bash', 'openvpn-install.sh'] + args, check=True, text=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.stderr)

@app.get("/")
def read_root():
    return {"message": "Welcome to the OpenVPN management API"}

@app.post("/install")
def install_openvpn(args: InstallArgs, username: str = Depends(get_current_user)):
    if os.path.exists("/etc/openvpn/server/server.conf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OpenVPN is already installed.")

    script_args = [
        args.ipv4_address or "",
        args.public_ip or "",
        args.protocol,
        str(args.port),
        str(args.dns),
        args.client_name
    ]
    output = run_script_with_args(script_args)
    return {"message": "OpenVPN installed successfully", "output": output}

@app.post("/add-client")
def add_client(client: Client, username: str = Depends(get_current_user)):
    output = run_script_with_args(['1', client.name])
    return {"message": f"Client {client.name} added successfully", "output": output}

@app.post("/revoke-client")
def revoke_client(client: Client, username: str = Depends(get_current_user)):
    output = run_script_with_args(['2', client.name])
    return {"message": f"Client {client.name} revoked successfully", "output": output}

@app.delete("/remove")
def remove_openvpn(username: str = Depends(get_current_user)):
    output = run_script_with_args(['3'])
    return {"message": "OpenVPN removed successfully", "output": output}

