from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import random
from blockfrost_api.get_trans import get_metadata_from_tx
from mqtt import connect
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

content = ""
with open("templates/index.html") as f:
    lines = f.readlines()
    for line in lines:
        content += line

def create_app():
    app = FastAPI()
    connect.run()
    @app.get("/", response_class=HTMLResponse)
    async def root():
        return HTMLResponse(content=content, status_code=200)

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                metadata = get_metadata_from_tx()
                if metadata:
                    await websocket.send_json(metadata)
                await asyncio.sleep(300)  # Gửi dữ liệu mỗi 10 giây
        except WebSocketDisconnect:
            print("WebSocket connection closed")
    return app

app = create_app()