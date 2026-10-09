# App access control

The backend can search its configured index using its own managed identity. Those
permissions do not authenticate browser users. The WebSocket `/realtime` endpoint
therefore rejects requests by default, and the Azure Container App has internal
ingress until Microsoft Entra authentication is configured.

## Enable authenticated browser access

1. Deploy once with the default private ingress to obtain the Container App
   hostname. In your tenant, register a **single-tenant** Microsoft Entra web
   application with the redirect URI
   `https://<container-app-hostname>/.auth/login/aad/callback`. Create a client
   secret and restrict sign-in to the intended users (for example, require user
   assignment on the Enterprise application and assign only authorized users).
   Use the deployment tenant for the app registration and enable ID tokens for
   web sign-in as described in the
   [Container Apps Entra setup guide](https://learn.microsoft.com/azure/container-apps/authentication-entra).
   Authentication alone does not restrict access to a subset of tenant users.
2. Set `AZURE_CONTAINER_APP_AUTH_CLIENT_ID` and
   `AZURE_CONTAINER_APP_AUTH_CLIENT_SECRET` in the deployment environment, using
   a secure secret store and keeping the secret out of source control and logs.
   Redeploy to enable external ingress and Container Apps authentication.
   Both values are required; otherwise ingress stays internal and `/realtime`
   remains unavailable. Rotate and update the secret before it expires.
3. Open the app over HTTPS and sign in. Container Apps' authentication sidecar
   requires authentication for **all** requests (including the WebSocket
   handshake), redirects unauthenticated browser navigation to Entra, and
   injects identity headers for the backend after validation. The browser sends
   its authenticated session cookie during the same-origin WebSocket handshake.
   The backend rejects missing or malformed identities and cross-origin
   WebSocket handshakes before connecting to Azure OpenAI.

The identity headers are **not signed by the app** and are trustworthy only
when all traffic passes through Container Apps' authentication sidecar with
the required-authentication policy. Never expose the backend's container port
directly, disable that policy, or set `VOICE_RAG_AUTH_MODE=container_apps`
behind an unauthenticated proxy: a caller could forge identity headers.
Do not treat CORS as authentication. If using a different host/proxy, implement
independent token validation and an authorization policy for that host before
making the service public.

For local development only, the server binds to `localhost`; setting
`VOICE_RAG_ALLOW_ANONYMOUS_LOCAL=true` explicitly enables local loopback
WebSocket access. It is rejected with `RUNNING_IN_PRODUCTION`, and it must not
be used with a forwarded port, a shared development environment, or private
index contents.

## Realtime model compatibility

The original sample uses the `gpt-4o-realtime-preview` deployment and its
date-versioned preview API. Where only a GA realtime deployment is available,
set `AZURE_OPENAI_REALTIME_MODEL=gpt-realtime-mini`,
`AZURE_OPENAI_REALTIME_DEPLOYMENT_VERSION=2025-10-06`, and
`AZURE_OPENAI_REALTIME_API_MODE=ga` before provisioning; choose a
[supported region and model version](https://learn.microsoft.com/azure/foundry/openai/how-to/realtime-audio).
The middle tier then connects to `/openai/v1/realtime` and adapts the session
audio configuration and event names for the existing browser client. When
reusing an existing Azure OpenAI account, set the existing deployment name
as usual and select the API mode that deployment supports. This setting does
not replace visitor authentication or open the Container App's ingress.
