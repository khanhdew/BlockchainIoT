import json
import logging
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
from pydantic import BaseModel
from fastapi import Request

from app.blockfrost_api.get_trans import get_metadata_from_tx, get_latest_tx
from app.mqtt import connect
from app.hashing_service.encrypt import EncryptModel

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
content = ""
ecrypt = EncryptModel()

with open("app/templates/index.html") as f:
    lines = f.readlines()
    for line in lines:
        content += line

with open("key.key") as f:
    origin_key = f.read().strip()


class KeyCheckRequest(BaseModel):
    key: str


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_roles: Dict[str, str] = {}  # Map session IDs to roles (master or user)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        if websocket.client.host in self.connection_roles:
            del self.connection_roles[websocket.client.host]

    async def send_personal_message(self, message, websocket: WebSocket):
        await websocket.send_json(message)

    def set_role(self, client_host: str, role: str):
        self.connection_roles[client_host] = role

    def get_role(self, client_host: str):
        return self.connection_roles.get(client_host, "user")


manager = ConnectionManager()


def create_app():
    app = FastAPI()
    connect.run()

    @app.get("/", response_class=HTMLResponse)
    async def root():
        return HTMLResponse(content=content, status_code=200)

    # POST URL "check_key" to authenticate the user and assign a role
    @app.post("/check_key")
    async def check_key(request: Request, key_request: KeyCheckRequest):
        # Lấy địa chỉ IP của client từ request
        client_host = request.client.host

        # Kiểm tra key
        if key_request.key == origin_key:
            # Đánh dấu kết nối này là "master" dựa trên địa chỉ IP của client
            manager.set_role(client_host, "master")
            return {"status": "valid"}
        else:
            raise HTTPException(status_code=400, detail="Invalid key")

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        client_host = websocket.client.host
        await manager.connect(websocket)

        try:
            # Check the role based on the HTTP POST verification
            role = manager.get_role(client_host)

            while True:
                metadatas = await get_metadata_from_tx(await get_latest_tx())

                # If the user is the master, decrypt data before sending
                if role == "master":
                    decrypted_data = ecrypt.decrypt(metadatas)
                    metadatas = json.loads(decrypted_data)

                # Send the first 15 metadata
                await manager.send_personal_message({"metadata": metadatas[:15]}, websocket)

                # Send the remaining metadata one by one
                for metadata in metadatas[15:]:
                    await manager.send_personal_message({"metadata": [metadata]}, websocket)
                    await asyncio.sleep(5)

                await asyncio.sleep(225)

        except WebSocketDisconnect:
            logger.info("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Error in WebSocket connection: {str(e)}")
        finally:
            manager.disconnect(websocket)

    return app


app = create_app()
