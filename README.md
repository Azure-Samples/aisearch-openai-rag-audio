# 🎙️ VoiceRAG: Azure OpenAI Realtime API + RAG with Arabic Support

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&skip_quickstart=true&machine=basicLinux32gb&repo=860141324&devcontainer_path=.devcontainer%2Fdevcontainer.json&geo=WestUs2)
[![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Azure-Samples/aisearch-openai-rag-audio)

An advanced voice-enabled application demonstrating the integration of **Azure OpenAI Realtime API** with **Retrieval-Augmented Generation (RAG)** using **Azure AI Search**. Features a unique 3-stage audio sequence, Arabic language support, and intelligent conversation capabilities.

## 🌟 Key Features

- 🎵 **3-Stage Audio Sequence** - Professional audio flow before voice conversation
- 🗣️ **Real-time Voice Chat** - Powered by Azure OpenAI Realtime API  
- 🔍 **Arabic RAG Search** - Native Arabic language support with Azure AI Search
- ⚡ **Instant Responses** - Sub-200ms search performance
- 🎯 **Smart Suggestions** - Contextual recommendations and error handling
- 📱 **Modern UI** - React/TypeScript interface with real-time visualizations

## 🎵 Unique Audio Experience

### The 3-Stage Audio Flow
```
🟣 User Clicks Purple Button
        ↓
🎵 Ran.mp3 (System Start - 3 seconds)
        ↓  
🔔 between.wav (Transition - 1 second)
        ↓
🎤 Nancy.wav (Welcome - 2 seconds)
        ↓
🚀 Azure OpenAI Realtime API Activated
        ↓
💬 Voice Conversation Ready
```

This creates a professional, engaging experience that smoothly transitions users from a static interface to dynamic voice conversation.

## 🏗️ Architecture Overview

![Architecture diagram showing the 3-stage audio sequence and RAG integration](docs/RTMTPattern.png)

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React Frontend │◄──►│  Python Backend  │◄──►│  Azure Services │
│                 │    │                  │    │                 │
│ • Audio Player  │    │ • WebSocket      │    │ • OpenAI Realtime│
│ • Voice Input   │    │ • RAG Tools      │    │ • AI Search     │
│ • UI Components │    │ • Static Server  │    │ • Arabic Data   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Core Components

1. **Frontend (React/TypeScript)**
   - Custom audio sequence player
   - Real-time voice recording and playback
   - Interactive UI with status indicators

2. **Backend (Python/aiohttp)**
   - WebSocket server for real-time communication
   - RAG tools integration with Azure AI Search
   - Static file serving for audio assets

3. **Azure Services**
   - OpenAI Realtime API for voice conversation
   - AI Search for Arabic knowledge retrieval
   - Secure authentication and API management

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** with pip
- **Node.js 18+** with npm
- **Azure subscription** with:
  - Azure OpenAI Realtime API access
  - Azure AI Search service
- **Git** for version control

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/AliArabi55/aisearch-openai-rag-audio
cd aisearch-openai-rag-audio

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install backend dependencies
cd app/backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install
npm run build
```

### 3. Configure Environment

Create `.env` file in `app/backend/`:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-mini-realtime-preview
AZURE_OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_REALTIME_VOICE_CHOICE=alloy

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_INDEX=your-index-name
AZURE_SEARCH_API_KEY=your_search_api_key

# RAG Configuration
AZURE_SEARCH_IDENTIFIER_FIELD=ID
AZURE_SEARCH_TITLE_FIELD=Name
AZURE_SEARCH_CONTENT_FIELD=ingredients
AZURE_SEARCH_USE_VECTOR_QUERY=false
```

### 4. Prepare Audio Files

Ensure these audio files are in `app/backend/static/audio/`:
- `Ran.mp3` - System startup sound (3 seconds)
- `between.wav` - Transition sound (1 second)  
- `Nancy.wav` - Welcome message (2 seconds)

### 5. Run the Application

```bash
# From app/backend directory
cd app/backend
python app.py
```

Open your browser to: **http://localhost:8765**

## 🎯 How to Use

1. **🟣 Click the purple button** to start the audio sequence
2. **🎵 Listen to the 3-sound sequence** (takes ~6 seconds total)
3. **🎤 Start speaking** when the ready indicator appears
4. **💬 Have a conversation** in Arabic or English
5. **🔍 Ask about products**: "أبحث عن بيتزا فراخ كرسبي" or "Show me crispy chicken pizza"
6. **📊 Get detailed responses** with prices, ingredients, and suggestions

## 🔍 Arabic RAG Capabilities

### Sample Interactions

**Arabic Query:**
```
User: "عايز أطلب كالزونى فراخ كرسبي كبير"

Response: 
🍽️ [1] كالزونى فراخ كرسبي كبير
المكونات: صلصه - فلفل - زيتون - موتزريلا - فراخ كرسبي  
السعر: 180 جنيه
```

**English Query:**
```
User: "I want crispy chicken calzone"

Response:
🍽️ [1] Crispy Chicken Calzone Large
Ingredients: Sauce - Peppers - Olives - Mozzarella - Crispy Chicken
Price: 180 EGP
```

### Smart Search Features

- **Multi-language support** - Arabic and English queries
- **Partial matching** - "فراخ" finds all chicken items
- **Context awareness** - Understands intent and preferences
- **Smart suggestions** - Recommendations when no exact matches

## 📊 Sample Data Structure

The application works with structured menu data:

```json
{
  "ID": "1",
  "Name": "كالزونى فراخ كرسبي كبير",
  "ingredients": "صلصه - فلفل - زيتون - موتزريلا - فراخ كرسبي",
  "Price": "180"
}
```

Supports various food categories:
- **Pizza** (بيتزا): Various toppings and sizes
- **Burgers** (برجر): Beef, chicken, specialty options
- **Calzones** (كالزونى): Different fillings and sizes
- **Sides** (مقبلات): Onion rings, appetizers

## 🛠️ Development Guide

### Project Structure

```
aisearch-openai-rag-audio/
├── app/
│   ├── backend/              # Python aiohttp server
│   │   ├── app.py           # Main application entry
│   │   ├── ragtools.py      # RAG + Azure Search integration
│   │   ├── rtmt.py          # Realtime API middleware
│   │   └── static/          # Audio files & frontend build
│   │       ├── audio/       # Ran.mp3, between.wav, Nancy.wav
│   │       └── assets/      # React build output
│   └── frontend/            # React/TypeScript interface
│       ├── src/
│       │   ├── components/  # Audio player, voice recorder
│       │   ├── hooks/       # Audio sequence logic
│       │   └── types.ts     # TypeScript definitions
│       ├── package.json
│       └── vite.config.ts
├── data/                    # Sample Arabic restaurant data
├── infra/                   # Azure infrastructure (Bicep)
├── docs/                    # Documentation and diagrams
└── tests/                   # Test files and scripts
```

### Key Technologies

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Backend**: Python 3.12, aiohttp, asyncio
- **Audio**: Web Audio API, AudioWorklet, WebRTC
- **Azure Services**: OpenAI Realtime API, AI Search, Container Apps
- **Infrastructure**: Bicep templates, GitHub Actions

### Development Workflow

```bash
# Start development servers
cd app/frontend
npm run dev          # Frontend dev server (port 5173)

cd app/backend  
python app.py        # Backend server (port 8765)
```

## 📈 Performance Metrics

### Target Performance
- **Audio sequence duration**: 6 seconds total
- **Search response time**: < 200ms
- **Voice latency**: < 500ms end-to-end
- **Memory usage**: < 512MB total
- **Startup time**: < 3 seconds

### Monitoring
The application includes built-in performance monitoring:
- Audio sequence timing
- Search query performance
- WebSocket connection health
- Error rate tracking

## 🔧 Customization

### Audio Files
Replace default audio files with your own:
```bash
# Copy your custom audio files
cp your-startup.mp3 app/backend/static/audio/Ran.mp3
cp your-transition.wav app/backend/static/audio/between.wav
cp your-welcome.wav app/backend/static/audio/Nancy.wav
```

### Search Configuration
Modify search behavior in `ragtools.py`:
```python
# Custom search parameters
search_config = {
    "query_type": "simple",
    "search_mode": "any",
    "top": 10,  # More results
    "minimum_coverage": 80
}
```

### UI Customization
Update the React components in `app/frontend/src/components/` to match your brand and requirements.

## 🚀 Deployment Options

### 1. Azure Container Apps (Recommended)
```bash
# Deploy to Azure using provided infrastructure
azd up
```

### 2. Docker Deployment
```bash
# Build and run with Docker
docker build -t voicerag-app .
docker run -p 8765:8765 voicerag-app
```

### 3. Manual Deployment
Deploy to any cloud provider supporting Python web applications.

## 📖 Documentation

### Complete Guides
- 📋 **[Arabic Documentation](README_Arabic.md)** - Complete guide in Arabic
- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - Detailed system architecture
- 🎵 **[Audio Features](AUDIO_FEATURES.md)** - Audio sequence implementation
- 🔧 **[Technical Guide](TECHNICAL_GUIDE.md)** - Advanced technical details

### API References
- **Azure OpenAI Realtime API**: [Official Documentation](https://learn.microsoft.com/azure/ai-services/openai/realtime-audio-quickstart)
- **Azure AI Search**: [Search API Reference](https://docs.microsoft.com/azure/search/)

## 🎯 Use Cases and Applications

### 🍕 Smart Restaurant Ordering
- Voice-based menu navigation
- Multi-language order taking
- Real-time inventory checking
- Order customization and upselling

### 🛒 E-commerce Voice Shopping
- Product discovery through conversation
- Voice-activated search and filtering
- Personalized recommendations
- Hands-free shopping experience

### 📚 Knowledge Base Assistant
- Voice-powered information retrieval
- Multi-language support
- Contextual follow-up questions
- Real-time fact checking

### 🏢 Customer Service Automation
- Intelligent call routing
- Multi-language support
- Knowledge base integration
- Escalation to human agents

## 🔮 Roadmap and Future Features

### Version 2.0 (Planned)
- [ ] **Multi-language expansion** - English, French, Spanish support
- [ ] **Voice emotion detection** - Sentiment analysis and adaptive responses
- [ ] **Custom voice models** - Personalized voice experiences
- [ ] **Advanced analytics** - Usage patterns and conversation insights

### Version 3.0 (Future)
- [ ] **Offline mode** - Local processing for sensitive environments
- [ ] **Integration APIs** - Easy integration with external systems
- [ ] **White-label solution** - Customizable for different industries
- [ ] **Mobile applications** - Native iOS and Android apps

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute
1. **🐛 Bug Reports** - Report issues and help improve stability
2. **💡 Feature Requests** - Suggest new capabilities and improvements  
3. **📝 Documentation** - Help improve guides and examples
4. **🔧 Code Contributions** - Submit pull requests with enhancements
5. **🌍 Translations** - Add support for additional languages

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/aisearch-openai-rag-audio
cd aisearch-openai-rag-audio

# Create feature branch
git checkout -b feature/your-feature-name

# Make your changes and test thoroughly
# Submit a pull request with clear description
```

### Code Standards
- Follow existing code style and patterns
- Add tests for new functionality
- Update documentation for changes
- Ensure all tests pass before submitting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- React: MIT License
- Azure SDK: MIT License
- Other dependencies: See package.json files

## 🆘 Support and Community

### Getting Help
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AliArabi55/aisearch-openai-rag-audio/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/AliArabi55/aisearch-openai-rag-audio/discussions)
- 📖 **Documentation**: [Project Wiki](https://github.com/AliArabi55/aisearch-openai-rag-audio/wiki)
- 💡 **Feature Requests**: [GitHub Issues](https://github.com/AliArabi55/aisearch-openai-rag-audio/issues)

### Community Guidelines
- Be respectful and inclusive
- Help others learn and grow
- Share knowledge and experiences
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)

## 🙏 Acknowledgments

### Special Thanks
- **Azure OpenAI Team** - For the incredible Realtime API
- **Azure AI Search Team** - For excellent Arabic language support
- **Open Source Community** - For inspiration and collaboration
- **Contributors** - Everyone who helps improve this project

### Built With
- [Azure OpenAI](https://azure.microsoft.com/products/ai-services/openai-service) - Realtime voice capabilities
- [Azure AI Search](https://azure.microsoft.com/products/search) - Intelligent search with Arabic support
- [React](https://reactjs.org/) - Frontend user interface
- [Python](https://www.python.org/) - Backend server implementation

---

## 🌟 Star History

If you find this project helpful, please consider giving it a star! ⭐

**Made with ❤️ for the global developer community**

*Experience the future of voice AI with seamless multilingual conversation and intelligent search capabilities.*

---

*Last updated: September 2025 | Version 1.0.0*

    [![Open in Dev Containers](https://img.shields.io/static/v1?style=for-the-badge&label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/azure-samples/aisearch-openai-rag-audio)
3. In the VS Code window that opens, once the project files show up (this may take several minutes), open a new terminal, and proceed to [deploying the app](#deploying-the-app).

### Local environment

1. Install the required tools:
   * [Azure Developer CLI](https://aka.ms/azure-dev/install)
   * [Node.js](https://nodejs.org/)
   * [Python >=3.11](https://www.python.org/downloads/)
      * **Important**: Python and the pip package manager must be in the path in Windows for the setup scripts to work.
      * **Important**: Ensure you can run `python --version` from console. On Ubuntu, you might need to run `sudo apt install python-is-python3` to link `python` to `python3`.
   * [Git](https://git-scm.com/downloads)
   * [Powershell](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) - For Windows users only.

2. Clone the repo (`git clone https://github.com/Azure-Samples/aisearch-openai-rag-audio`)
3. Proceed to the next section to [deploy the app](#deploying-the-app).

## Deploying the app

The steps below will provision Azure resources and deploy the application code to Azure Container Apps.

1. Login to your Azure account:

    ```shell
    azd auth login
    ```

    For GitHub Codespaces users, if the previous command fails, try:

   ```shell
    azd auth login --use-device-code
    ```

1. Create a new azd environment:

    ```shell
    azd env new
    ```

    Enter a name that will be used for the resource group.
    This will create a new folder in the `.azure` folder, and set it as the active environment for any calls to `azd` going forward.

1. (Optional) This is the point where you can customize the deployment by setting azd environment variables, in order to [use existing services](docs/existing_services.md) or [customize the voice choice](docs/customizing_deploy.md).

1. Run this single command to provision the resources, deploy the code, and setup integrated vectorization for the sample data:

   ```shell
   azd up
   ````

   * **Important**: Beware that the resources created by this command will incur immediate costs, primarily from the AI Search resource. These resources may accrue costs even if you interrupt the command before it is fully executed. You can run `azd down` or delete the resources manually to avoid unnecessary spending.
   * You will be prompted to select two locations, one for the majority of resources and one for the OpenAI resource, which is currently a short list. That location list is based on the [OpenAI model availability table](https://learn.microsoft.com/azure/ai-services/openai/concepts/models#global-standard-model-availability) and may become outdated as availability changes.

1. After the application has been successfully deployed you will see a URL printed to the console.  Navigate to that URL to interact with the app in your browser. To try out the app, click the "Start conversation button", say "Hello", and then ask a question about your data like "What is the whistleblower policy for Contoso electronics?" You can also now run the app locally by following the instructions in [the next section](#development-server).

## Development server

You can run this app locally using either the Azure services you provisioned by following the [deployment instructions](#deploying-the-app), or by pointing the local app at already [existing services](docs/existing_services.md).

1. If you deployed with `azd up`, you should see a `app/backend/.env` file with the necessary environment variables.

2. If did *not* use `azd up`, you will need to create `app/backend/.env` file with the following environment variables:

   ```shell
   AZURE_OPENAI_ENDPOINT=wss://<your instance name>.openai.azure.com
   AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview
   AZURE_OPENAI_REALTIME_VOICE_CHOICE=<choose one: echo, alloy, shimmer>
   AZURE_OPENAI_API_KEY=<your api key>
   AZURE_SEARCH_ENDPOINT=https://<your service name>.search.windows.net
   AZURE_SEARCH_INDEX=<your index name>
   AZURE_SEARCH_API_KEY=<your api key>
   ```

   To use Entra ID (your user when running locally, managed identity when deployed) simply don't set the keys.

3. Run this command to start the app:

   Windows:

   ```pwsh
   pwsh .\scripts\start.ps1
   ```

   Linux/Mac:

   ```bash
   ./scripts/start.sh
   ```

4. The app is available on [http://localhost:8765](http://localhost:8765).

   Once the app is running, when you navigate to the URL above you should see the start screen of the app:
   ![app screenshot](docs/talktoyourdataapp.png)

   To try out the app, click the "Start conversation button", say "Hello", and then ask a question about your data like "What is the whistleblower policy for Contoso electronics?"

## Guidance

### Costs

Pricing varies per region and usage, so it isn't possible to predict exact costs for your usage.
However, you can try the [Azure pricing calculator](https://azure.com/e/a87a169b256e43c089015fda8182ca87) for the resources below.

* Azure Container Apps: Consumption plan with 1 CPU core, 2.0 GB RAM. Pricing with Pay-as-You-Go. [Pricing](https://azure.microsoft.com/pricing/details/container-apps/)
* Azure OpenAI: Standard tier, gpt-4o-realtime and text-embedding-3-large models. Pricing per 1K tokens used. [Pricing](https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/)
* Azure AI Search: Standard tier, 1 replica, free level of semantic search. Pricing per hour. [Pricing](https://azure.microsoft.com/pricing/details/search/)
* Azure Blob Storage: Standard tier with ZRS (Zone-redundant storage). Pricing per storage and read operations. [Pricing](https://azure.microsoft.com/pricing/details/storage/blobs/)
* Azure Monitor: Pay-as-you-go tier. Costs based on data ingested. [Pricing](https://azure.microsoft.com/pricing/details/monitor/)

To reduce costs, you can switch to free SKUs for various services, but those SKUs have limitations.

⚠️ To avoid unnecessary costs, remember to take down your app if it's no longer in use,
either by deleting the resource group in the Portal or running `azd down`.

### Security

This template uses [Managed Identity](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) to eliminate the need for developers to manage these credentials. Applications can use managed identities to obtain Microsoft Entra tokens without having to manage any credentials.To ensure best practices in your repo we recommend anyone creating solutions based on our templates ensure that the [Github secret scanning](https://docs.github.com/code-security/secret-scanning/about-secret-scanning) setting is enabled in your repos.

### Notes

>Sample data: The PDF documents used in this demo contain information generated using a language model (Azure OpenAI Service). The information contained in these documents is only for demonstration purposes and does not reflect the opinions or beliefs of Microsoft. Microsoft makes no representations or warranties of any kind, express or implied, about the completeness, accuracy, reliability, suitability or availability with respect to the information contained in this document. All rights reserved to Microsoft.

## Resources

* [Blog post: VoiceRAG](https://aka.ms/voicerag)
* [Demo video: VoiceRAG](https://youtu.be/vXJka8xZ9Ko)
* [Azure OpenAI Realtime Documentation](https://github.com/Azure-Samples/aoai-realtime-audio-sdk/)