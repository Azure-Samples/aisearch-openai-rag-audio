import base64
import json
import os
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer, make_mocked_request
from azure.core.credentials import AzureKeyCredential

from rtmt import RTMiddleTier
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


if __name__ == "__main__":
    unittest.main()
