# Instructions for Coding Agents

This file contains instructions for developers and automated coding agents working on the VoiceRAG application. It covers code layout, environment setup, testing procedures, and development conventions.

## Overview

VoiceRAG is an application pattern demonstrating RAG (Retrieval Augmented Generation) with voice interfaces using Azure AI Search and the GPT-4o Realtime API for Audio. The application enables voice-based interactions with a knowledge base, with audio input processed through the browser and sent to Azure OpenAI's real-time API for responses.

**Main technologies:**
- **Backend**: Python 3.11+ with aiohttp web framework
- **Frontend**: React with TypeScript, built with Vite
- **Infrastructure**: Azure Bicep templates for Azure Container Apps deployment
- **Key Azure Services**: Azure OpenAI (GPT-4o Realtime API), Azure AI Search, Azure Container Apps
- **Deployment**: Azure Developer CLI (azd)

**Primary entry points:**
- `app/backend/app.py` - Backend application server (aiohttp)
- `app/frontend/src/main.tsx` - Frontend React application
- `scripts/start.sh` or `scripts/start.ps1` - Development server startup scripts

## Code layout

- `app/` - Main application code
  - `app/backend/` - Python backend code
    - `app/backend/app.py` - Main entry point for backend server (aiohttp)
    - `app/backend/rtmt.py` - Real-time middle tier for Azure OpenAI integration
    - `app/backend/ragtools.py` - RAG tools for Azure AI Search integration
    - `app/backend/setup_intvect.py` - Setup script for integrated vectorization
    - `app/backend/requirements.txt` - Python dependencies
  - `app/frontend/` - React TypeScript frontend
    - `app/frontend/src/` - Source code for React components
    - `app/frontend/src/locales/` - Translation files (en, es, fr, ja)
    - `app/frontend/package.json` - Node.js dependencies
    - `app/frontend/vite.config.ts` - Vite build configuration
  - `app/Dockerfile` - Container image definition for deployment
- `infra/` - Bicep infrastructure-as-code templates
  - `infra/main.bicep` - Main infrastructure definition
  - `infra/main.parameters.json` - Template parameters
  - `infra/core/` - Reusable Bicep modules
- `scripts/` - Helper scripts for development and deployment
  - `scripts/start.sh` / `scripts/start.ps1` - Start development server
  - `scripts/write_env.sh` / `scripts/write_env.ps1` - Generate .env file from azd
  - `scripts/setup_intvect.sh` / `scripts/setup_intvect.ps1` - Setup integrated vectorization
  - `scripts/load_python_env.sh` / `scripts/load_python_env.ps1` - Create Python virtual environment
- `data/` - Sample data files (Markdown documents)
- `docs/` - Documentation
  - `docs/existing_services.md` - Connect to existing Azure services
  - `docs/customizing_deploy.md` - Customize deployment options
  - `docs/manual_setup.md` - Manual setup instructions
- `.github/workflows/` - GitHub Actions workflows
  - `.github/workflows/template-validation.yaml` - Template validation workflow
  - `.github/workflows/azure-dev.yml` - Azure deployment workflow
- `azure.yaml` - Azure Developer CLI (azd) configuration
- `pyproject.toml` - Python project configuration (ruff linting rules)

## Running the code

### Prerequisites

Install the required tools:
- [Azure Developer CLI](https://aka.ms/azure-dev/install)
- [Node.js](https://nodejs.org/) (for frontend)
- [Python 3.11 or higher](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

**Important for Windows users:**
- Python and pip must be in PATH
- [PowerShell](https://learn.microsoft.com/powershell/scripting/install/installing-powershell) is required

### Local development setup

1. **Create and activate Python virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r app/backend/requirements.txt
   ```

3. **Install frontend dependencies:**
   ```bash
   cd app/frontend
   npm install
   cd ../..
   ```

4. **Configure environment variables:**
   
   After deploying with `azd up`, the `.env` file is automatically created at `app/backend/.env`.
   
   If running locally without azd deployment, create `app/backend/.env` with:
   ```
   AZURE_TENANT_ID=<your-tenant-id>
   AZURE_OPENAI_ENDPOINT=https://<your-openai-service>.openai.azure.com
   AZURE_OPENAI_REALTIME_DEPLOYMENT=gpt-4o-realtime-preview
   AZURE_OPENAI_REALTIME_VOICE_CHOICE=alloy
   AZURE_SEARCH_ENDPOINT=https://<your-search-service>.search.windows.net
   AZURE_SEARCH_INDEX=<your-index-name>
   AZURE_SEARCH_SEMANTIC_CONFIGURATION=default
   AZURE_SEARCH_IDENTIFIER_FIELD=chunk_id
   AZURE_SEARCH_CONTENT_FIELD=chunk
   AZURE_SEARCH_TITLE_FIELD=title
   AZURE_SEARCH_EMBEDDING_FIELD=text_vector
   AZURE_SEARCH_USE_VECTOR_QUERY=true
   ```

   To use Entra ID authentication (recommended), omit API keys. The app will use:
   - `AzureDeveloperCliCredential` when running locally with azd
   - `DefaultAzureCredential` otherwise
   - Managed Identity when deployed to Azure

5. **Start the development server:**
   
   **Linux/Mac:**
   ```bash
   ./scripts/start.sh
   ```
   
   **Windows:**
   ```powershell
   pwsh .\scripts\start.ps1
   ```

6. **Access the application:**
   
   Open [http://localhost:8765](http://localhost:8765) in your browser.

### Deploying to Azure

1. **Authenticate with Azure:**
   ```bash
   azd auth login
   # For GitHub Codespaces, use: azd auth login --use-device-code
   ```

2. **Create a new environment:**
   ```bash
   azd env new
   ```
   Enter a name for your resource group.

3. **(Optional) Customize deployment:**
   
   Before running `azd up`, you can configure:
   - [Reuse existing Azure services](docs/existing_services.md)
   - [Customize voice choice](docs/customizing_deploy.md)
   
   Example:
   ```bash
   azd env set AZURE_OPENAI_REALTIME_VOICE_CHOICE shimmer
   ```

4. **Provision and deploy:**
   ```bash
   azd up
   ```
   
   This command will:
   - Provision Azure resources (OpenAI, Search, Container Apps, etc.)
   - Build and deploy the application container
   - Setup integrated vectorization for sample data
   
   **Warning**: This will incur Azure costs. Run `azd down` to delete resources when done.

5. **Update local .env file after deployment:**
   
   After `azd up` completes, synchronize local environment:
   ```bash
   ./scripts/write_env.sh  # Linux/Mac
   pwsh ./scripts/write_env.ps1  # Windows
   ```

## Running the tests

**Note**: This repository does not currently have automated tests. When adding tests, follow these guidelines:

### Setting up test infrastructure (future)

If you need to add tests:

1. **Install test dependencies:**
   ```bash
   pip install pytest pytest-asyncio pytest-cov
   ```

2. **Run tests:**
   ```bash
   source .venv/bin/activate  # Ensure virtualenv is active
   pytest -q
   ```

3. **Run tests with coverage:**
   ```bash
   pytest --cov=app/backend --cov-report=term-missing
   ```

### Frontend testing (future)

When adding frontend tests:

```bash
cd app/frontend
npm test
```

## Upgrading Python dependencies

### Adding a new dependency

1. **Edit `app/backend/requirements.txt`:**
   ```
   # Add new package with version pin
   new-package==1.2.3
   ```

2. **Install the updated dependencies:**
   ```bash
   source .venv/bin/activate  # Ensure virtualenv is active
   pip install -r app/backend/requirements.txt
   ```

3. **Test the changes:**
   - Run the development server to ensure no breakage
   - Test functionality that uses the new dependency

### Upgrading an existing dependency

1. **Update version in `app/backend/requirements.txt`:**
   ```
   # Change version
   package-name==2.0.0  # was 1.0.0
   ```

2. **Install and test:**
   ```bash
   pip install -r app/backend/requirements.txt
   # Test the application thoroughly
   ```

**Note**: This project uses direct pip with pinned versions in `requirements.txt`. Unlike some projects that use `uv` or `pip-compile` with separate `.in` files, dependencies are managed directly in `requirements.txt`.

## Release / build / deployment notes

### Azure deployment with azd

The primary deployment method is Azure Developer CLI (azd):

```bash
azd up  # Provision infrastructure and deploy application
```

Key deployment files:
- `azure.yaml` - Defines azd configuration and hooks
- `infra/main.bicep` - Infrastructure as Code template
- `app/Dockerfile` - Container image definition

### Post-provision hooks

After infrastructure provisioning, azd automatically runs:
- `scripts/write_env.sh` / `scripts/write_env.ps1` - Generate .env file
- `scripts/setup_intvect.sh` / `scripts/setup_intvect.ps1` - Setup integrated vectorization

### Container deployment

The app is deployed to Azure Container Apps. The build happens via:
- Remote build on Azure (configured in `azure.yaml`)
- Container registry created during deployment
- Image built from `app/Dockerfile`

### CI/CD workflows

- `.github/workflows/azure-dev.yml` - Automated Azure deployment
- `.github/workflows/template-validation.yaml` - Template validation (internal use)

## Conventions & gotchas

### Code style and linting

**Python:**
- Linting configured in `pyproject.toml` using Ruff
- Target version: Python 3.9+
- Rules: E (errors), F (pyflakes), I (import order), UP (pyupgrade)
- Ignored: E501 (line length), E701 (multiple statements)

**Check Python code style:**
```bash
# Install ruff if not already installed
pip install ruff

# Run linting
ruff check app/backend
```

**Frontend:**
- TypeScript with strict type checking
- Prettier for formatting

**Format frontend code:**
```bash
cd app/frontend
npm run format
```

### Environment variables

**Required environment variables:**
- `AZURE_TENANT_ID` - Azure tenant ID
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI service endpoint
- `AZURE_OPENAI_REALTIME_DEPLOYMENT` - Deployment name for GPT-4o realtime
- `AZURE_OPENAI_REALTIME_VOICE_CHOICE` - Voice selection (alloy, echo, shimmer)
- `AZURE_SEARCH_ENDPOINT` - Azure AI Search endpoint
- `AZURE_SEARCH_INDEX` - Search index name

**Optional environment variables:**
- `AZURE_OPENAI_API_KEY` - Use key auth instead of Entra ID
- `AZURE_SEARCH_API_KEY` - Use key auth instead of Entra ID
- `RUNNING_IN_PRODUCTION` - Disable .env file loading when set

### Security considerations

- **Never commit secrets**: Use `.gitignore` to exclude `.env` files
- **Prefer managed identity**: Use Entra ID authentication over API keys
- **API keys**: If using keys, store them in Azure Key Vault or local .env only
- This template uses [Managed Identity](https://learn.microsoft.com/entra/identity/managed-identities-azure-resources/overview) for Azure services

### Common pitfalls

1. **Python version**: Must be 3.11 or higher. Check with `python --version`
2. **Virtual environment**: Always activate `.venv` before running pip or Python commands
3. **Node.js dependencies**: Run `npm install` in `app/frontend/` before building
4. **Frontend build**: Frontend builds into `app/backend/static/` directory
5. **Port conflicts**: Backend runs on port 8765 by default
6. **Azure costs**: Resources incur costs immediately after `azd up`. Clean up with `azd down`
7. **Real-time API availability**: GPT-4o realtime API is only available in specific regions (eastus2, swedencentral)
8. **WebSocket proxy**: Frontend dev server proxies `/realtime` to `ws://localhost:8765`

### File paths and structure

- Backend loads `.env` from `app/backend/.env`
- Frontend builds to `app/backend/static/`
- Static files served from backend at root path `/`
- WebSocket endpoint at `/realtime`

## Validation checklist

Before opening a pull request, complete this checklist:

- [ ] Virtual environment is activated (`.venv`)
- [ ] Python dependencies installed: `pip install -r app/backend/requirements.txt`
- [ ] Frontend dependencies installed: `cd app/frontend && npm install`
- [ ] Python code passes linting: `ruff check app/backend` (if ruff installed)
- [ ] Frontend code is formatted: `cd app/frontend && npm run format`
- [ ] Frontend builds successfully: `cd app/frontend && npm run build`
- [ ] Backend starts without errors: `python app/backend/app.py`
- [ ] No secrets or `.env` files committed
- [ ] No debug print statements or console.logs left in code
- [ ] Documentation updated if behavior changed (README.md, docs/)
- [ ] Environment variables documented if added (this file and docs/)
- [ ] Azure resource changes reflected in `infra/main.bicep` if applicable
- [ ] Testing performed:
  - [ ] Manual testing with development server
  - [ ] Voice interaction tested (if audio features changed)
  - [ ] Search functionality verified (if search features changed)

## When to search

This file is the primary reference for development practices and repository structure. **Trust the information in AGENTS.md first.**

Only perform source-wide searches (`grep`, `rg`, file exploration) when:
- Information in this file is missing or unclear
- You need to find specific implementation patterns not documented here
- You suspect this file is outdated and need to verify current code structure
- You need to locate all usages of a specific API or function
- You're debugging an issue that requires understanding code flow

For common tasks (setup, deployment, testing, linting), follow the instructions in this file without searching the codebase first.
