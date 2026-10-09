import asyncio
import base64
import json
import os
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer, make_mocked_request
from azure.core.credentials import AzureKeyCredential

from rtmt import RTMiddleTier, Tool, ToolResult, ToolResultDirection
from app import realtime_auth_mode


class RealtimeAccessTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tier = RTMiddleTier("https://example.invalid", "test", AzureKeyCredential("unused"))
        self.tier._forward_messages = AsyncMock()
        app = web.Application()
        self.tier.attach_to_app(app, "/realtime")
        self.client = TestClient(TestServer(app))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()

    async def handshake(self, headers=None):
        return await self.client.get("/realtime", headers={
            "Connection": "Upgrade",
            "Upgrade": "websocket",
            "Sec-WebSocket-Version": "13",
            "Sec-WebSocket-Key": "dGhlIHNhbXBsZSBub25jZQ==",
            **(headers or {}),
        })

    async def test_default_rejects_anonymous_before_upgrade(self):
        response = await self.handshake()
        self.assertEqual(response.status, 401)
        self.tier._forward_messages.assert_not_awaited()

    async def test_platform_mode_requires_valid_principal(self):
        self.tier.auth_mode = "container_apps"
        async def relay(ws):
            await ws.send_json({"type": "session.created"})

        self.tier._forward_messages.side_effect = relay
        principal = base64.b64encode(json.dumps({
            "auth_typ": "aad",
            "claims": [{"typ": "http://schemas.microsoft.com/identity/claims/objectidentifier",
                        "val": "user-1"}],
        }).encode()).decode()
        for headers in ({}, {"Authorization": "Bearer invalid-token"},
                        {"X-MS-TOKEN-AAD-ID-TOKEN": "invalid-token"},
                        {"X-MS-CLIENT-PRINCIPAL": "not-base64"},
                        {"X-MS-CLIENT-PRINCIPAL": "é"},
                        {"X-MS-CLIENT-PRINCIPAL": base64.b64encode(b"{}").decode()},
                        {"X-MS-CLIENT-PRINCIPAL": base64.b64encode(
                            b'{"auth_typ":"aad","claims":[]}').decode()}):
            with self.subTest(headers=headers):
                response = await self.handshake(headers)
                self.assertEqual(response.status, 401)
                self.tier._forward_messages.assert_not_awaited()

        ws = await self.client.ws_connect("/realtime", headers={
            "X-MS-CLIENT-PRINCIPAL": principal,
            "Origin": str(self.client.make_url("/realtime").origin()).replace("http:", "https:"),
        })
        self.assertEqual(await ws.receive_json(), {"type": "session.created"})
        await ws.close()
        self.tier._forward_messages.assert_awaited_once()

    async def test_cross_origin_handshake_is_rejected(self):
        self.tier.auth_mode = "container_apps"
        principal = base64.b64encode(json.dumps({
            "auth_typ": "aad",
            "claims": [{"typ": "oid", "val": "user-1"}],
        }).encode()).decode()
        response = await self.handshake({
            "X-MS-CLIENT-PRINCIPAL": principal,
            "Origin": "https://untrusted.example"
        })
        self.assertEqual(response.status, 403)
        self.tier._forward_messages.assert_not_awaited()

    async def test_local_anonymous_opt_in_only_accepts_loopback(self):
        self.tier.auth_mode = "local"
        ws = await self.client.ws_connect("/realtime")
        await ws.close()
        self.tier._forward_messages.assert_awaited_once()

        transport = Mock()
        transport.get_extra_info.return_value = ("203.0.113.1", 55555)
        remote_request = make_mocked_request("GET", "/realtime", transport=transport)
        with self.assertRaises(web.HTTPUnauthorized):
            await self.tier._websocket_handler(remote_request)

    async def test_wrong_identity_provider_is_rejected(self):
        self.tier.auth_mode = "container_apps"
        principal = base64.b64encode(json.dumps({
            "auth_typ": "anonymous", "claims": [{"typ": "oid", "val": "user-1"}]
        }).encode()).decode()
        response = await self.handshake({"X-MS-CLIENT-PRINCIPAL": principal})
        self.assertEqual(response.status, 401)
        self.tier._forward_messages.assert_not_awaited()


class ConfigurationTests(unittest.TestCase):
    def test_deployment_exposes_ingress_only_with_auth(self):
        root = Path(__file__).resolve().parents[2]
        main = (root / "infra" / "main.bicep").read_text(encoding="utf-8")
        module = (root / "infra" / "core" / "host" / "container-app.bicep").read_text(encoding="utf-8")
        params = json.loads((root / "infra" / "main.parameters.json").read_text(encoding="utf-8"))["parameters"]
        self.assertIn("!empty(authClientId) && !empty(authClientSecret)", main)
        self.assertIn("external: authConfigured", main)
        self.assertIn("VOICE_RAG_AUTH_MODE: authConfigured ? 'container_apps' : 'disabled'", main)
        self.assertIn("unauthenticatedClientAction: 'RedirectToLoginPage'", module)
        self.assertIn("openIdIssuer: '${environment().authentication.loginEndpoint}${authTenantId}/v2.0'", module)
        self.assertIn("authClientId", params)
        self.assertIn("authClientSecret", params)
        self.assertEqual(params["authClientId"]["value"], "${AZURE_CONTAINER_APP_AUTH_CLIENT_ID=}")
        self.assertEqual(params["authClientSecret"]["value"], "${AZURE_CONTAINER_APP_AUTH_CLIENT_SECRET=}")
        self.assertEqual(params["realtimeModelName"]["value"], "${AZURE_OPENAI_REALTIME_MODEL=gpt-4o-realtime-preview}")
        self.assertEqual(params["realtimeApiMode"]["value"], "${AZURE_OPENAI_REALTIME_API_MODE=preview}")
        self.assertIn("VOICE_RAG_REALTIME_API_MODE: realtimeApiMode", main)

    def test_authentication_defaults_to_disabled(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(realtime_auth_mode(), "disabled")

    def test_local_opt_in_is_rejected_in_production(self):
        with patch.dict(os.environ, {
            "RUNNING_IN_PRODUCTION": "true",
            "VOICE_RAG_ALLOW_ANONYMOUS_LOCAL": "true",
        }, clear=True):
            with self.assertRaises(ValueError):
                realtime_auth_mode()

    def test_invalid_authentication_configuration_is_rejected(self):
        with patch.dict(os.environ, {"VOICE_RAG_AUTH_MODE": "unknown"}, clear=True):
            with self.assertRaises(ValueError):
                realtime_auth_mode()
        with patch.dict(os.environ, {"VOICE_RAG_ALLOW_ANONYMOUS_LOCAL": "yes"}, clear=True):
            with self.assertRaises(ValueError):
                realtime_auth_mode()

    def test_local_opt_in_and_platform_mode(self):
        with patch.dict(os.environ, {"VOICE_RAG_ALLOW_ANONYMOUS_LOCAL": "true"}, clear=True):
            self.assertEqual(realtime_auth_mode(), "local")
        with patch.dict(os.environ, {"VOICE_RAG_AUTH_MODE": "container_apps"}, clear=True):
            self.assertEqual(realtime_auth_mode(), "container_apps")

    def test_invalid_realtime_api_mode_is_rejected(self):
        with self.assertRaises(ValueError):
            RTMiddleTier("https://example.invalid", "test", AzureKeyCredential("unused"),
                         realtime_api="unknown")


class RealtimeGATests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.received = []
        self.simulate_tool = False
        self.upstream = TestServer(web.Application())
        self.upstream.app.router.add_get("/openai/v1/realtime", self.fake_upstream)
        await self.upstream.start_server()

        self.tier = RTMiddleTier(str(self.upstream.make_url("/").origin()), "mini-canary",
                                 AzureKeyCredential("unused"), voice_choice="alloy",
                                 auth_mode="local", realtime_api="ga")
        self.tier.system_message = "Use the search tool."
        app = web.Application()
        self.tier.attach_to_app(app, "/realtime")
        self.client = TestClient(TestServer(app))
        await self.client.start_server()

    async def asyncTearDown(self):
        await self.client.close()
        await self.upstream.close()

    async def fake_upstream(self, request):
        self.assertEqual(request.query.get("model"), "mini-canary")
        self.assertNotIn("api-version", request.query)
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        await ws.send_json({"type": "session.created", "session": {
            "id": "canary-session", "instructions": "server-only", "tools": [],
            "audio": {"output": {"voice": "alloy"}},
        }})
        async for msg in ws:
            event = json.loads(msg.data)
            self.received.append(event)
            if event["type"] == "session.update":
                await ws.send_json({"type": "session.updated", "session": {"type": "realtime"}})
                if self.simulate_tool:
                    await ws.send_json({"type": "conversation.item.added",
                                        "previous_item_id": "item-1",
                                        "item": {"type": "function_call", "call_id": "call-1"}})
                    await ws.send_json({"type": "conversation.item.done",
                                        "item": {"type": "function_call", "call_id": "call-1"}})
                    await ws.send_json({"type": "response.output_item.done",
                                        "item": {"type": "function_call", "call_id": "call-1",
                                                 "name": "search", "arguments": '{"query":"canary"}'}})
                else:
                    await ws.send_json({"type": "response.output_audio.delta", "delta": "YQ=="})
        return ws

    async def test_ga_websocket_uses_supported_route_and_session_schema(self):
        ws = await self.client.ws_connect("/realtime")
        created = await ws.receive_json(timeout=5)
        self.assertEqual(created["type"], "session.created")
        self.assertEqual(created["session"]["instructions"], "")
        await ws.send_json({"type": "session.update", "session": {
            "turn_detection": {"type": "server_vad"}
        }})
        self.assertEqual((await ws.receive_json(timeout=5))["type"], "session.updated")
        audio = await ws.receive_json(timeout=5)
        self.assertEqual(audio, {"type": "response.audio.delta", "delta": "YQ=="})
        update = self.received[0]["session"]
        self.assertEqual(update["type"], "realtime")
        self.assertEqual(update["audio"]["input"]["turn_detection"]["type"], "server_vad")
        self.assertEqual(update["audio"]["output"]["voice"], "alloy")
        self.assertEqual(update["instructions"], "Use the search tool.")
        self.assertNotIn("voice", update)
        self.assertNotIn("turn_detection", update)
        await ws.close()

    async def test_ga_function_call_receives_search_result(self):
        self.simulate_tool = True
        search = AsyncMock(return_value=ToolResult("synthetic quince", ToolResultDirection.TO_SERVER))
        self.tier.tools = {"search": Tool(search, {"type": "function", "name": "search",
                                                   "parameters": {"type": "object", "properties": {}}})}
        ws = await self.client.ws_connect("/realtime")
        self.assertEqual((await ws.receive_json(timeout=5))["type"], "session.created")
        await ws.send_json({"type": "session.update", "session": {}})
        self.assertEqual((await ws.receive_json(timeout=5))["type"], "session.updated")
        for _ in range(10):
            if any(event["type"] == "conversation.item.create" for event in self.received):
                break
            await asyncio.sleep(0.02)
        outputs = [event for event in self.received if event["type"] == "conversation.item.create"]
        self.assertEqual(len(outputs), 1)
        self.assertEqual(outputs[0]["item"]["output"], "synthetic quince")
        search.assert_awaited_once_with({"query": "canary"})
        with self.assertRaises(asyncio.TimeoutError):
            await ws.receive_json(timeout=0.2)
        await ws.close()

if __name__ == "__main__":
    unittest.main()
