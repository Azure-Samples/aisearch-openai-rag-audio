# aisearch-openai-rag-audio

## Local development
1. Install the required tools:
   - [Node.js](https://nodejs.org/en)
1. Clone the repo.
1. **Temporary until backend is wired up**: in app/frontend/src/App.tsx replace
   ```
   const AOAI_ENDPOINT = "YOUR_INSTANCE_NAME.openai.azure.com";
   const AOAI_KEY = "YOUR_API_KEY";
   ```
1. Run this command to start the app:
   ```
   cd app
   pwsh .\start.ps1
   ```
1. To enable hot reloading of frontend, open a new terminal and run:
   ```
   cd app/frontend
   npm run dev
   ```
   You should see something like:
   ```
   VITE v5.4.6  ready in 536 ms

   ➜  Local:   http://127.0.0.1:5173/
   ➜  press h + enter to show help
   ```
   Navigate to the URL shown in the terminal (in this case, `http://127.0.0.1:5173/`). Whenever you make changes to frontend files, it'll automatically reload without needing a browser refresh.