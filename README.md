# VoiceRAG: An Application Pattern for RAG + Voice Using Azure AI Search and the GPT-4o Realtime API for Audio

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&skip_quickstart=true&machine=basicLinux32gb&repo=860141324&devcontainer_path=.devcontainer%2Fdevcontainer.json&geo=WestUs2)
[![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Azure-Samples/aisearch-openai-rag-audio)

This repo contains an example of how to implement RAG support in applications that use voice as their user interface, powered by the GPT-4o realtime API for audio. We describe the pattern in more detail in [this blog post](https://aka.ms/voicerag), and you can see this sample app in action in [this short video](https://youtu.be/vXJka8xZ9Ko).

![RTMTPattern](docs/RTMTPattern.png)

## Running this sample
We'll follow 4 steps to get this example running in your own environment: pre-requisites, creating an index, setting up the environment, and running the app.

### 1. Pre-requisites
You'll need instances of the following Azure services. You can re-use service instances you have already or create new ones.
1. [Azure OpenAI](https://ms.portal.azure.com/#create/Microsoft.CognitiveServicesOpenAI), with 2 model deployments, one of the **gpt-4o-realtime-preview** model, and one for embeddings (e.g.text-embedding-3-large, text-embedding-3-small, or text-embedding-ada-002)
1. [Azure AI Search](https://ms.portal.azure.com/#create/Microsoft.Search), any tier Basic or above will work, ideally with [Semantic Search enabled](https://learn.microsoft.com/azure/search/semantic-how-to-enable-disable)
1. [Azure Blob Storage](https://ms.portal.azure.com/#create/Microsoft.StorageAccount-ARM), with a container that has the content that represents your knowledge base (we include some sample data in this repo if you want an easy starting point)

### 2. Creating an index
RAG applications use a retrieval system to get the right grounding data for LLMs. We use Azure AI Search as our retrieval system, so we need to get our knowledge base (e.g. documents or any other content you want the app to be able to talk about) into an Azure AI Search index.

**If you already have an Azure AI Search index**

You can use an existing index directly. If you created that index using the "Import and vectorize data" option in the portal, no further changes are needed. Otherwise, you'll need to update the field names in the [code](https://github.com/Azure-Samples/aisearch-openai-rag-audio/blob/main/app/backend/ragtools.py) to match your text/vector fields.

**Creating a new index with sample data or your own**

Follow these steps to create a new index. We'll create a setup where once created, you can add, delete, or update your documents in blob storage and the index will automatically follow the changes.

1. Upload your documents to an Azure Blob Storage container. An easy way to do this is using the Azure Portal: navigate to the container and use the upload option to move your content (e.g. PDFs, Office docs, etc.)
1. In the Azure Portal, go to your Azure AI Search service and select "Import and vectorize data", choose Blob Storage, then point at your container and follow the rest of the steps on the screen.
1. Once the indexing process completes, you'll have a search index ready for vector and hybrid search.

For more details on ingesting data in Azure AI Search using "Import and vectorize data", here's a [quickstart](https://learn.microsoft.com/en-us/azure/search/search-get-started-portal-import-vectors).

### 3. Setting up the environment
The app needs to know which service endpoints to use for the Azure OpenAI and Azure AI Search. The following variables can be set as environment variables, or you can create a ".env" file in the "app/backend/" directory with this content.
   ```
   AZURE_OPENAI_ENDPOINT=wss://<your instance name>.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-realtime-preview
   AZURE_OPENAI_API_KEY=<your api key>
   AZURE_SEARCH_ENDPOINT=https://<your service name>.search.windows.net
   AZURE_SEARCH_INDEX=<your index name>
   AZURE_SEARCH_API_KEY=<your api key>
   ```
   To use Entra ID (your user when running locally, managed identity when deployed) simply don't set the keys. 

### 4. Running the app

#### GitHub Codespaces
You can run this repo virtually by using GitHub Codespaces, which will open a web-based VS Code in your browser:

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&skip_quickstart=true&machine=basicLinux32gb&repo=860141324&devcontainer_path=.devcontainer%2Fdevcontainer.json&geo=WestUs2)

Once the codespace opens (this may take several minutes), open a new terminal.

#### VS Code Dev Containers
You can run the project in your local VS Code Dev Container using the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers):

1. Start Docker Desktop (install it if not already installed)
2. Open the project:

    [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/azure-samples/aisearch-openai-rag-audio)
3. In the VS Code window that opens, once the project files show up (this may take several minutes), open a new terminal.

#### Local environment
1. Install the required tools:
   - [Node.js](https://nodejs.org/en)
   - [Python >=3.11](https://www.python.org/downloads/)
      - **Important**: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
      - **Important**: Ensure you can run `python --version` from console. On Ubuntu, you might need to run `sudo apt install python-is-python3` to link `python` to `python3`.
   - [Powershell](https://learn.microsoft.com/powershell/scripting/install/installing-powershell)

2. Clone the repo (`git clone https://github.com/Azure-Samples/aisearch-openai-rag-audio`)
4. The app needs to know which service endpoints to use for the Azure OpenAI and Azure AI Search. The following variables can be set as environment variables, or you can create a ".env" file in the "app/backend/" directory with this content.
   ```
   AZURE_OPENAI_ENDPOINT=wss://<your instance name>.openai.azure.com
   AZURE_OPENAI_DEPLOYMENT=gpt-4o-realtime-preview
   AZURE_OPENAI_API_KEY=<your api key>
   AZURE_SEARCH_ENDPOINT=https://<your service name>.search.windows.net
   AZURE_SEARCH_INDEX=<your index name>
   AZURE_SEARCH_API_KEY=<your api key>
   ```
   To use Entra ID (your user when running locally, managed identity when deployed) simply don't set the keys.  
5. Run this command to start the app:

   Windows:

   ```pwsh
   cd app
   pwsh .\start.ps1
   ```

   Linux/Mac:

   ```bash
   cd app
   ./start.sh
   ```

6. The app is available on http://localhost:8765

Once the app is running, when you navigate to the URL above you should see the start screen of the app:
![app screenshot](docs/talktoyourdataapp.png)

### Frontend: enabling direct communication with AOAI Realtime API
You can make the frontend skip the middle tier and talk to the websockets AOAI Realtime API directly, if you choose to do so. However note this'll stop RAG from happening, and will requiring exposing your API key in the frontend which is very insecure. DO NOT use this in production.

Just Pass some extra parameters to the `useRealtime` hook:
```typescript
const { startSession, addUserAudio, inputAudioBufferClear } = useRealTime({
        useDirectAoaiApi: true,
        aoaiEndpointOverride: "wss://<NAME>.openai.azure.com",
        aoaiApiKeyOverride: "<YOUR API KEY, INSECURE!!!>",
        aoaiModelOverride: "gpt-4o-realtime-preview",
        ...
);
```

### Notes

>Sample data: The PDF documents used in this demo contain information generated using a language model (Azure OpenAI Service). The information contained in these documents is only for demonstration purposes and does not reflect the opinions or beliefs of Microsoft. Microsoft makes no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the information contained in this document. All rights reserved to Microsoft.