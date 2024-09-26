# aisearch-openai-rag-audio

## Local development
1. Install the required tools:
   - [Node.js](https://nodejs.org/en)
   - [Python >=3.10](https://www.python.org/downloads/)
      - **Important**: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
      - **Important**: Ensure you can run `python --version` from console. On Ubuntu, you might need to run `sudo apt install python-is-python3` to link `python` to `python3`.
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