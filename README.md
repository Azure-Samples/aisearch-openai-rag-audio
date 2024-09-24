# aisearch-openai-rag-audio

## Local development
1. Install the required tools:
   - [Node.js](https://nodejs.org/en)
1. Clone the repo.
1. Create `app/backend/.env` with:
   ```
   AZURE_OPENAI_ENDPOINT=wss://<your instance name>.openai.azure.com
   AZURE_OPENAI_API_KEY=<your api key>
   AZURE_SEARCH_ENDPOINT=https://<your service name>.search.windows.net
   AZURE_SEARCH_INDEX=<your index name>
   AZURE_SEARCH_API_KEY=<your api key>
   ```
1. Run this command to start the app:
   ```
   cd app
   pwsh .\start.ps1
   ```
1. The app is available on http://localhost:8765