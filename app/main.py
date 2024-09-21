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
from starlette.middleware.cors import CORSMiddleware

from app.blockfrost_api.get_trans import get_metadata_from_tx, get_latest_tx
from app.mqtt import connect
from app.hashing_service.encrypt import EncryptModel
from app.database.connector import Connector

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
content = ""
ecrypt = EncryptModel()
conn = Connector()

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
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_roles: Dict[str, str] = {}
        self.permission_requests: Dict[str, bool] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        self.active_connections[client_id] = websocket

    def disconnect(self, websocket: WebSocket):
        client_id = None
        for cid, ws in self.active_connections.items():
            if ws == websocket:
                client_id = cid
                break
        if client_id:
            del self.active_connections[client_id]

    def get_role(self, client_id: str):
        return self.connection_roles.get(client_id)

    def set_role(self, client_id: str, role: str):
        self.connection_roles[client_id] = role

    def request_permission(self, client_id: str):
        self.permission_requests[client_id] = False

    def grant_permission(self, client_id: str):
        self.permission_requests[client_id] = True

    def has_permission(self, client_id: str):
        return self.permission_requests.get(client_id)

    def get_owner(self):
        for client_id, role in self.connection_roles.items():
            if role == "master":
                return client_id
        return None

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)


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
        client_id = request.headers.get('client_id')

        if key_request.key == origin_key:
            manager.set_role(client_id, "master")
            return {"status": "valid"}
        else:
            raise HTTPException(status_code=400, detail="Invalid key")

    @app.post("/request_permission")
    async def request_permission(request: Request):
        client_id = request.headers.get('client_id')
        manager.request_permission(client_id)
        owner = manager.get_owner()
        if owner:
            owner_ws = manager.active_connections.get(owner)
            if owner_ws:
                await manager.send_personal_message({"request": client_id}, owner_ws)
        return {"status": "requested"}

    @app.post("/handle_request_response")
    async def handle_request_response(request: Request, response: dict):
        client_id = request.headers.get('client_id')
        action = response.get('action')
        requester_id = response.get('client_id')
        print(f"Action: {action}, requester: {requester_id}")
        if action == "approve":
            manager.grant_permission(requester_id)
            requester_ws = manager.active_connections.get(requester_id)
            if requester_ws:
                await manager.send_personal_message({"approved": True}, requester_ws)
        return {"status": "handled"}

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        data = await websocket.receive_json()
        client_id = data.get('client_id')
        print(f"Client {client_id} connected")
        await manager.connect(websocket, client_id)

        try:
            while True:
                tx_hash = await get_latest_tx()
                metadatas = await get_metadata_from_tx(tx_hash)

                role = manager.get_role(client_id)
                if role != "master" and not manager.has_permission(client_id):
                    await manager.send_personal_message({"permission": "not authorized"}, websocket)

                if role == "master" or manager.has_permission(client_id):
                    cursor = conn.execute(f"SELECT \"hash_key\".hash FROM \"transaction\" inner join \"hash_key\" "
                                          f"on \"transaction\".hash_key = \"hash_key\".id "
                                          f"WHERE \"transaction\".hash = '{tx_hash}'")
                    hash_key = None
                    for row in cursor:
                        hash_key = row[0]
                    decrypted_data = ecrypt.decrypt(metadatas, key=hash_key)
                    metadatas = json.loads(decrypted_data)
                else:
                    if isinstance(metadatas, str):
                        metadatas = json.loads(metadatas)

                await manager.send_personal_message({"metadata": metadatas[:int(len(metadatas) / 2)]}, websocket)

                for metadata in metadatas[int(len(metadatas) / 2):]:
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
