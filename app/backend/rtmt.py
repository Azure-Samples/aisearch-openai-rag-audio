import asyncio
import json
import logging
from enum import Enum
from typing import Any, Callable, Optional

import aiohttp
from aiohttp import web
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Set up logging
logger = logging.getLogger("voicerag")

# Enum for tool result direction


class ToolResultDirection(Enum):
    TO_SERVER = 1
    TO_CLIENT = 2

# Class to encapsulate tool results


class ToolResult:
    text: str
    destination: ToolResultDirection

    def __init__(self, text: str, destination: ToolResultDirection):
        self.text = text
        self.destination = destination

    # Convert result to text
    def to_text(self) -> str:
        if self.text is None:
            return ""
        return self.text if type(self.text) == str else json.dumps(self.text)

# Class to represent a tool


class Tool:
    target: Callable[..., ToolResult]
    schema: Any

    def __init__(self, target: Any, schema: Any):
        self.target = target
        self.schema = schema

# Class to track tool calls


class RTToolCall:
    tool_call_id: str
    previous_id: str

    def __init__(self, tool_call_id: str, previous_id: str):
        self.tool_call_id = tool_call_id
        self.previous_id = previous_id

# Main class for real-time middle tier


class RTMiddleTier:
    endpoint: str
    deployment: str
    key: Optional[str] = None

    # Dictionary to store tools
    tools: dict[str, Tool] = {}

    # Server-enforced configuration options
    model: Optional[str] = None
    system_message: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    disable_audio: Optional[bool] = None
    voice_choice: Optional[str] = None
    api_version: str = "2024-10-01-preview"
    # api_version: str = "2024-12-17-preview"
    _tools_pending = {}
    _token_provider = None

    def __init__(self, endpoint: str, deployment: str, credentials: AzureKeyCredential | DefaultAzureCredential, voice_choice: Optional[str] = None):
        self.endpoint = endpoint
        self.deployment = deployment
        self.voice_choice = voice_choice
        if voice_choice is not None:
            logger.info("Realtime voice choice set to %s", voice_choice)
        if isinstance(credentials, AzureKeyCredential):
            self.key = credentials.key
        else:
            self._token_provider = get_bearer_token_provider(
                credentials, "https://cognitiveservices.azure.com/.default")
            # Warm up during startup so we have a token cached when the first request arrives
            self._token_provider()

    # Process messages sent to the client
    async def _process_message_to_client(self, msg: str, client_ws: web.WebSocketResponse, server_ws: web.WebSocketResponse) -> Optional[str]:

        message = json.loads(msg.data)
        updated_message = msg.data
        if message is not None:
            match message["type"]:
                case "session.created":
                    session = message["session"]
                    # Hide the instructions, tools and max tokens from clients
                    session["instructions"] = ""
                    session["tools"] = []
                    session["voice"] = self.voice_choice
                    session["tool_choice"] = "none"
                    session["max_response_output_tokens"] = None
                    updated_message = json.dumps(message)

                case "response.output_item.added":
                    if "item" in message and message["item"]["type"] == "function_call":
                        updated_message = None

                case "conversation.item.created":
                    if "item" in message and message["item"]["type"] == "function_call":
                        item = message["item"]
                        if item["call_id"] not in self._tools_pending:
                            self._tools_pending[item["call_id"]] = RTToolCall(
                                item["call_id"], message["previous_item_id"])
                        updated_message = None
                    elif "item" in message and message["item"]["type"] == "function_call_output":
                        updated_message = None

                case "response.function_call_arguments.delta":
                    updated_message = None

                case "response.function_call_arguments.done":
                    updated_message = None

                case "response.output_item.done":
                    if "item" in message and message["item"]["type"] == "function_call":
                        item = message["item"]
                        tool_call = self._tools_pending[message["item"]["call_id"]]
                        tool = self.tools[item["name"]]
                        args = item["arguments"]
                        result = await tool.target(json.loads(args))
                        await server_ws.send_json({
                            "type": "conversation.item.create",
                            "item": {
                                "type": "function_call_output",
                                "call_id": item["call_id"],
                                "output": result.to_text() if result.destination == ToolResultDirection.TO_SERVER else ""
                            }
                        })
                        if result.destination == ToolResultDirection.TO_CLIENT:
                            # Send tool result to client
                            await client_ws.send_json({
                                "type": "extension.middle_tier_tool_response",
                                "previous_item_id": tool_call.previous_id,
                                "tool_name": item["name"],
                                "tool_result": result.to_text()
                            })
                        updated_message = None

                case "response.done":
                    if len(self._tools_pending) > 0:
                        self._tools_pending.clear()  # Clear pending tool calls
                        await server_ws.send_json({
                            "type": "response.create"
                        })
                    if "response" in message:
                        replace = False
                        for i, output in enumerate(reversed(message["response"]["output"])):
                            if output["type"] == "function_call":
                                message["response"]["output"].pop(i)
                                replace = True
                        if replace:
                            updated_message = json.dumps(message)

        return updated_message

    # Process messages sent to the server
    async def _process_message_to_server(self, msg: str, ws: web.WebSocketResponse) -> Optional[str]:

        if isinstance(msg, aiohttp.WSMessage):
            message = json.loads(msg.data)
            updated_message = msg.data
        else:
            message = json.loads(msg)
            updated_message = msg

        if message is not None:
            match message["type"]:
                case "session.update":
                    session = message["session"]
                    if self.system_message is not None:
                        session["instructions"] = self.system_message
                    if self.temperature is not None:
                        session["temperature"] = self.temperature
                    if self.max_tokens is not None:
                        session["max_response_output_tokens"] = self.max_tokens
                    if self.disable_audio is not None:
                        session["disable_audio"] = self.disable_audio
                    if self.voice_choice is not None:
                        session["voice"] = self.voice_choice
                    session["tool_choice"] = "auto" if len(
                        self.tools) > 0 else "none"
                    session["tools"] = [
                        tool.schema for tool in self.tools.values()]
                    updated_message = json.dumps(message)

        return updated_message

    # Forward messages between client and server
    async def _forward_messages(self, ws: web.WebSocketResponse):
        async with aiohttp.ClientSession(base_url=self.endpoint) as session:
            params = {"api-version": self.api_version,
                      "deployment": self.deployment}
            headers = {}
            if "x-ms-client-request-id" in ws.headers:
                headers["x-ms-client-request-id"] = ws.headers["x-ms-client-request-id"]
            if self.key is not None:
                headers = {"api-key": self.key}
            else:
                # NOTE: no async version of token provider, maybe refresh token on a timer?
                headers = {"Authorization": f"Bearer {self._token_provider()}"}
            async with session.ws_connect("/openai/realtime", headers=headers, params=params) as target_ws:
                # Function to handle messages from client to server
                async def from_client_to_server():

                    async for msg in ws:

                        if (type(msg) == aiohttp.WSMessage):
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                new_msg = await self._process_message_to_server(msg, ws)
                                if new_msg is not None:
                                    await target_ws.send_str(new_msg)
                            else:
                                print("Error: unexpected message type:", msg.type)
                        else:

                            new_msg = await self._process_message_to_server(msg, ws)

                            if new_msg is not None:
                                await target_ws.send_str(new_msg)

                    # Close the target_ws if client closes connection
                    if target_ws:
                        print("Closing OpenAI's realtime socket connection.")
                        await target_ws.close()

                # Function to handle messages from server to client
                async def from_server_to_client():
                    async for msg in target_ws:

                        if (type(msg) == aiohttp.WSMessage):
                            if msg.type == aiohttp.WSMsgType.TEXT:
                                new_msg = await self._process_message_to_client(msg, ws, target_ws)
                                if new_msg is not None:
                                    await ws.send_str(new_msg)
                            else:
                                print("Error: unexpected message type:", msg.type)

                        else:
                            new_msg = await self._process_message_to_client(msg, ws, target_ws)
                            if new_msg is not None:
                                await ws.send_str(new_msg)

                try:
                    await asyncio.gather(from_client_to_server(), from_server_to_client())
                except ConnectionResetError:
                    # Ignore errors from client disconnecting
                    pass

    # WebSocket handler
    async def _websocket_handler(self, request: web.Request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await self._forward_messages(ws)
        return ws

    # Attach WebSocket handler to app
    def attach_to_app(self, app, path):
        app.router.add_get(path, self._websocket_handler)

    # Attach WebSocket handler to WebSocket
    async def attach_to_websocket(self, ws):
        print("attach_to_websocket")
        await self._forward_messages(ws)
