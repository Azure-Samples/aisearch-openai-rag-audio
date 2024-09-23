import aiohttp
import asyncio
import json
from typing import Any, Optional
from aiohttp import web

class Tool:
    target: Any
    schema: Any

    def __init__(self, target: Any, schema: Any):
        self.target = target
        self.schema = schema

class RTToolCall:
    message_id: str
    conversation: str
    tool_call_id: str
    name: str
    arguments: str

class RTMiddleTier:
    endpoint: str
    key: str

    # Tools are server-side only for now, though the case could be made for client-side tools
    # in addition to server-side tools that are invisible to the client
    tools: dict[str, Tool] = {}

    # Server-enforced configuration, if set, these will override the client's configuration
    # Typically at least the model name and system message will be set by the server
    model: Optional[str] = None
    system_message: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    disable_audio: Optional[bool] = None

    _tool_calls: dict[str, RTToolCall] = {}

    def __init__(self, endpoint: str, key: str):
        self.endpoint = endpoint
        self.key = key

    async def _process_message(self, msg: str, server_ws: web.WebSocketResponse, to_client: bool) -> Optional[str]:
        message = json.loads(msg.data)
        updated_message = msg.data
        if message is not None:
            match message["event"]:
                case "update_conversation_config":
                    if not to_client:
                        if self.system_message is not None:
                            message["system_message"] = self.system_message
                        if self.temperature is not None:
                            message["temperature"] = self.temperature
                        if self.max_tokens is not None:
                            message["max_tokens"] = self.max_tokens
                        if self.disable_audio is not None:
                            message["disable_audio"] = self.disable_audio
                        message["tool_choice"] = "auto" if len(self.tools) > 0 else "none"
                        message["tools"] = [tool.schema for tool in self.tools.values()]
                        updated_message = json.dumps(message)

                case "add_message":
                    if to_client:
                        # Not sure if its possible for an add_message event to contain a mix of tools and non-tools calls,
                        # accounting for it just in case
                        remove_indexes = []
                        for i, submsg in enumerate(message["message"]["content"]):
                            if submsg["type"] == "tool_call":
                                remove_indexes.append(i)
                                tool_call: RTToolCall = RTToolCall()
                                tool_call.message_id = message["message"]["id"]
                                tool_call.conversation = message["conversation_label"]
                                tool_call.name = submsg["name"]
                                tool_call.tool_call_id = submsg["tool_call_id"]
                                tool_call.arguments = submsg["arguments"]
                                self._tool_calls[tool_call.message_id] = tool_call
                        if len(remove_indexes) < len(message["message"]["content"]):
                            for i in reversed(remove_indexes):
                                message["message"]["content"].pop(i)
                            updated_message = json.dumps(message)
                        else:
                            updated_message = None

                case "add_content":
                    if to_client and message["type"] == "tool_call":
                        tool_call = self._tool_calls[message["message_id"]]
                        tool_call.arguments += message["data"]
                        updated_message = None

                case "message_added":
                    if to_client:
                        tool_call = self._tool_calls.get(message["id"])
                        if tool_call is not None:
                            # TODO, validate which to use, message["content"][0]["arguments"] seems to have a repeat of the arguments
                            tool = self.tools[tool_call.name]
                            result = await tool.target(json.loads(tool_call.arguments))
                            # TODO: validate with full spec for tool response
                            await server_ws.send_str(json.dumps({
                                "event": "add_message",
                                "conversation_label": tool_call.conversation,
                                "message": {
                                    "role": "tool",
                                    "tool_call_id": tool_call.tool_call_id,
                                    "content": [{
                                        "type": "text",
                                        "text": result if type(result) == str else json.dumps(result)
                                    }]
                                }
                            }))
                            updated_message = None

                case "generation_finished":
                    if len(self._tool_calls) > 0:
                        await server_ws.send_str(json.dumps({
                            "event": "generate"
                        }))
                        self._tool_calls.clear()
            
        return updated_message

    async def _forward_messages(self, ws: web.WebSocketResponse):
        async with aiohttp.ClientSession(base_url=self.endpoint) as session:
            params = { "api-version": "alpha" }
            headers = { "api-key": self.key }
            if "x-ms-client-request-id" in ws.headers:
                headers["x-ms-client-request-id"] = ws.headers["x-ms-client-request-id"]
            async with session.ws_connect("/realtime", headers=headers, params=params) as target_ws:
                async def from_client_to_server():
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            new_msg = await self._process_message(msg, target_ws, to_client=False)
                            if new_msg is not None:
                                await target_ws.send_str(new_msg)
                        else:
                            print("Error: unexpected message type:", msg.type)

                async def from_server_to_client():
                    async for msg in target_ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            new_msg = await self._process_message(msg, target_ws, to_client=True)
                            if new_msg is not None:
                                await ws.send_str(new_msg)
                        else:
                            print("Error: unexpected message type:", msg.type)

                try:
                    await asyncio.gather(from_client_to_server(), from_server_to_client())
                except ConnectionResetError:
                    # Ignore the errors resulting from the client disconnecting the socket
                    pass

    async def _websocket_handler(self, request: web.Request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await self._forward_messages(ws)
        return ws
    
    def attach_to_app(self, app, path):
        app.router.add_get(path, self._websocket_handler)
