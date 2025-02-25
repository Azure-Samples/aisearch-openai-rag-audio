from fastapi import WebSocket, WebSocketDisconnect


class WebSocketAdapter:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.headers = websocket.headers

    async def send_str(self, data: str):
        await self.websocket.send_text(data)

    async def send_json(self, data: dict):
        await self.websocket.send_json(data)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            data = await self.websocket.receive_text()
            return data
        except WebSocketDisconnect:
            raise StopAsyncIteration
