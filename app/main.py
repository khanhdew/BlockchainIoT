from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio

from humanfriendly.terminal import message

from app.blockfrost_api.get_trans import get_metadata_from_tx, get_two_latest_tx, get_latest_tx
from app.mqtt import connect

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")
content = ""
with open("app/templates/index.html") as f:
    lines = f.readlines()
    for line in lines:
        content += line

def create_app():
    app = FastAPI()
    connect.run()
    @app.get("/", response_class=HTMLResponse)
    async def root():
        return HTMLResponse(content=content, status_code=200)

    @app.post("/checkkey")
    async def check_key(key: str):
        if key == "123":
            return {"status": "success"}
        else:
            return {"status": "failed"}
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await websocket.accept()
        # initChart_txHashes = get_two_latest_tx()
        # initChart_metadatas = []
        # for tx in initChart_txHashes:
        #     initChart_metadatas.append(get_metadata_from_tx(tx))
        # isInited = False
        try:
            while True:
                # if not isInited:
                #     await websocket.send_json(initChart_metadatas[0])
                #     await asyncio.sleep(5)
                #     # for metadata in initChart_metadatas[0]:
                #     #     sensorData = [metadata]
                #     #     await websocket.send_json(sensorData)
                #     #     initChart_metadatas.clear()
                #     #     await asyncio.sleep(5)
                #     isInited = True
                # else:
                metadatas = get_metadata_from_tx(get_latest_tx())
                await websocket.send_json(metadatas[0:15])
                del metadatas[:15]
                for metadata in metadatas:
                    sensorData = [metadata]
                    await websocket.send_json(sensorData)
                    await asyncio.sleep(5)
                await asyncio.sleep(225)
        except WebSocketDisconnect:
            print("WebSocket connection closed")
        except:
            pass
    return app

app = create_app()