# 🎙️ Azure OpenAI Realtime API with RAG & Azure AI Search - Arabic Enhanced

[![Open in GitHub Codespaces](https://img.shields.io/static/v1?style=for-the-badge&label=GitHub+Codespaces&message=Open&color=brightgreen&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&skip_quickstart=true&machine=basicLinux32gb&repo=860141324&devcontainer_path=.devcontainer%2Fdevcontainer.json&geo=WestUs2)

A cutting-edge voice-enabled application that combines **Azure OpenAI Realtime API** with **Retrieval-Augmented Generation (RAG)** using **Azure AI Search** for intelligent Arabic conversations. Features a unique 3-stage audio sequence before activating real-time voice chat.

## 🌟 Features

- 🎵 **3-Stage Audio Sequence** - Ran.mp3 → between.wav → Nancy.wav → Realtime API
- 🗣️ **Arabic Voice Conversation** - Full Arabic language support with Azure OpenAI
- 🔍 **Smart RAG Search** - Real-time search in Arabic knowledge base
- ⚡ **Instant Responses** - < 200ms response time with context-aware answers
- 🎯 **Smart Suggestions** - Helpful suggestions when no results found

## 🎵 Audio Flow: 3 Sounds + Realtime

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

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React Frontend │◄──►│  Python Backend  │◄──►│  Azure Services │
│                 │    │                  │    │                 │
│ • Audio Player  │    │ • WebSocket      │    │ • OpenAI Realtime│
│ • Voice Input   │    │ • RAG Tools      │    │ • AI Search     │
│ • UI Components │    │ • Static Server  │    │ • Arabic Data   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Azure OpenAI Realtime API access
- Azure AI Search service

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/AliArabi55/aisearch-openai-rag-audio
cd aisearch-openai-rag-audio

# 2. Install backend dependencies
cd app/backend
pip install -r requirements.txt

# 3. Install frontend dependencies
cd ../frontend
npm install
npm run build

# 4. Configure environment variables
cd ../backend
cp .env.example .env
# Edit .env with your Azure credentials
```

### Configuration

Create `.env` file in `app/backend/` with:

```env
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com
AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-mini-realtime-preview
AZURE_OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_REALTIME_VOICE_CHOICE=alloy
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_INDEX=your-index-name
AZURE_SEARCH_API_KEY=your_search_api_key
AZURE_SEARCH_IDENTIFIER_FIELD=ID
AZURE_SEARCH_TITLE_FIELD=Name
AZURE_SEARCH_CONTENT_FIELD=ingredients
AZURE_SEARCH_USE_VECTOR_QUERY=false
```

### Run the Application

```bash
# From app/backend directory
python app.py
```

Visit: `http://localhost:8765`

## 🎯 How to Use

1. **Click the purple button** 🟣 to start the audio sequence
2. **Listen to the 3-sound sequence** (takes ~6 seconds total)
3. **Start speaking** when the ready indicator appears
4. **Ask questions in Arabic** like:
   - "أبحث عن بيتزا فراخ كرسبي"
   - "عايز أطلب كالزونى فراخ باربكيو"
   - "اعرض كل المنتجات"
5. **Get instant voice responses** with product details and prices

## 🔍 RAG Features

### Arabic-First Search
- **No translation required** - Direct Arabic text processing
- **Smart partial matching** - "فراخ" finds all chicken items
- **Context-aware results** - Understands intent and context

### Sample Search Results
```
🍽️ [1] كالزونى فراخ كرسبي كبير
المكونات: صلصه - فلفل - زيتون - موتزريلا - فراخ كرسبي
السعر: 180 جنيه
-----
```

## 📊 Sample Data Structure

The system works with Arabic restaurant menu data:

```json
{
  "ID": "1",
  "Name": "كالزونى فراخ كرسبي كبير", 
  "ingredients": "صلصه - فلفل - زيتون - موتزريلا - فراخ كرسبي",
  "Price": "180"
}
```

## 📁 Project Structure

```
aisearch-openai-rag-audio/
├── app/
│   ├── backend/              # Python aiohttp server
│   │   ├── app.py           # Main application
│   │   ├── ragtools.py      # RAG + Azure Search integration  
│   │   ├── rtmt.py          # Realtime API middleware
│   │   └── static/          # Audio files & frontend build
│   │       ├── audio/       # Ran.mp3, between.wav, Nancy.wav
│   │       └── assets/      # React build output
│   └── frontend/            # React/TypeScript interface
│       ├── src/
│       │   ├── components/  # Audio player, voice recorder
│       │   └── hooks/       # Audio sequence logic
│       └── package.json
├── data/                    # Sample Arabic data
├── infra/                   # Azure infrastructure (Bicep)
└── README_Arabic.md         # Complete Arabic documentation
```

## 🔧 Key Components

### 🎤 Audio System
- **Sequential audio playback** with smooth transitions
- **WebSocket real-time communication** with Azure OpenAI
- **High-quality audio processing** (24kHz/16-bit)

### 🔍 RAG Integration  
- **Azure AI Search** with Arabic language support
- **Smart query processing** for natural language understanding
- **Contextual response enhancement** with product details

### 🌐 Frontend Interface
- **React/TypeScript** with modern UI components
- **Real-time audio visualization** and status indicators
- **Responsive design** for desktop and mobile

## 🌍 Internationalization

- **Arabic-first design** - Native Arabic text processing
- **RTL support** - Right-to-left text rendering
- **Cultural adaptation** - Localized number formatting and currency

## 📖 Documentation

- 📋 **[Complete Arabic README](README_Arabic.md)** - Detailed documentation in Arabic
- 🏗️ **[Architecture Guide](ARCHITECTURE.md)** - System architecture and data flow
- 🎵 **[Audio Features Guide](AUDIO_FEATURES.md)** - Audio sequence implementation

## 🎯 Use Cases

- 🍕 **Smart Restaurant Ordering** - Voice-based menu browsing and ordering
- 🛒 **E-commerce Voice Search** - Product discovery through natural conversation  
- 📚 **Knowledge Base Q&A** - Voice-powered information retrieval
- 🏪 **Retail Assistant** - In-store voice help and product recommendations

## ⚙️ Advanced Configuration

### Search Optimization
```python
# Custom search configuration for Arabic
search_config = {
    "query_type": "simple",
    "search_mode": "any", 
    "analyzer": "ar.microsoft",
    "highlight_fields": ["Name", "ingredients"]
}
```

### Audio Sequence Customization
```javascript
// Modify audio sequence in frontend
const audioSequence = [
  { file: "Ran.mp3", duration: 3000 },
  { file: "between.wav", duration: 1000 }, 
  { file: "Nancy.wav", duration: 2000 }
];
```

## 🚀 Deployment

### Azure Container Apps (Recommended)
```bash
# Deploy to Azure using provided infrastructure
azd up
```

### Docker Deployment
```bash
# Build and run with Docker
docker build -t voicerag-app .
docker run -p 8765:8765 voicerag-app
```

### Manual Deployment
```bash
# Install dependencies and run
pip install -r app/backend/requirements.txt
cd app/frontend && npm install && npm run build
cd ../backend && python app.py
```

## 🔮 Future Enhancements

- [ ] **Multi-language support** - Add English, French, Spanish
- [ ] **Voice emotion analysis** - Detect user sentiment and adapt responses
- [ ] **Custom audio personas** - Multiple voice options and personalities
- [ ] **Advanced analytics** - Usage tracking and conversation insights
- [ ] **Offline mode** - Local processing for sensitive environments

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Set up development environment
git clone https://github.com/AliArabi55/aisearch-openai-rag-audio
cd aisearch-openai-rag-audio
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r app/backend/requirements.txt
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/AliArabi55/aisearch-openai-rag-audio/issues)
- 💬 **Questions**: [GitHub Discussions](https://github.com/AliArabi55/aisearch-openai-rag-audio/discussions)
- 📖 **Documentation**: [Wiki](https://github.com/AliArabi55/aisearch-openai-rag-audio/wiki)

## 🙏 Acknowledgments

- Azure OpenAI team for the amazing Realtime API
- Azure AI Search team for excellent Arabic language support
- The open-source community for inspiration and contributions

---

**Made with ❤️ for the Arabic developer community** 🇦🇪

*Experience the future of voice AI with seamless Arabic conversation and intelligent search*

---

*Last updated: September 2025*
