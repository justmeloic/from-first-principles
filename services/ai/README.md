# From First Principles - AI Service

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Google ADK](https://img.shields.io/badge/Google_ADK-1.5.0+-4285F4.svg)
![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?logo=google-cloud&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_AI-00B4D8?logo=ollama&logoColor=white)

AI backend service for the From First Principles platform, providing intelligent chat capabilities and semantic content indexing powered by Google's Gemini models, local Ollama models, and modern vector search technology.

## Overview

This service provides a comprehensive AI platform with two main components:

### 🤖 Chat API Service

A FastAPI-based backend that powers intelligent chat functionality with:

- **Multi-Model Support**: Choose between Google Gemini models or local Ollama models
- **Session Management**: Persistent conversation history across multiple interactions
- **CORS Configuration**: Secure cross-origin requests from the frontend
- **Static File Serving**: Integrated frontend serving capabilities
- **Production Ready**: Deployment scripts and production configurations

### 📚 Content Indexing System

A modern semantic search pipeline that transforms your blog content into an intelligent, searchable knowledge base:

- **🧠 Dual Search Modes**: Semantic search using AI embeddings for conceptual matching, plus traditional keyword search for exact terms
- **⚡ High Performance**: Vector similarity using LanceDB with GPU acceleration and intelligent caching
- **🎨 Modern CLI**: Beautiful `index-cli` interface with rich terminal output, progress tracking, and comprehensive help
- **🔧 Developer Friendly**: Complete Python API, detailed statistics, error handling, and extensive documentation
- **📊 Smart Processing**: Automatic text chunking, metadata extraction, and embedding generation with 384-dimensional vectors

**How it Works**: The system processes your markdown blog posts, splits them into semantic chunks, generates AI embeddings using sentence transformers, and stores everything in a high-performance vector database. This enables both conceptual similarity search ("find posts about machine learning") and exact keyword matching ("find posts mentioning 'LanceDB'").

**Perfect For**: Content discovery, research assistance, finding related articles, and building intelligent search experiences for your blog readers.

👀 **For complete technical details, architecture diagrams, and API documentation**, see the [**Indexing System Documentation**](src/indexing/README.md).

## Architecture

```mermaid
graph TD
    A[Frontend - fromfirstprinciple.com] --> B[AI Service API]
    A --> K[Content Search]

    B --> C[Google ADK Session Management]
    B --> D{Model Provider}
    C --> E[In-Memory Session Store]
    D --> F[Gemini Models]
    D --> G[Ollama Models]
    F --> H[Vertex AI / Google AI Studio]
    G --> I[Local Ollama Server]

    K --> L[Indexing Pipeline]
    L --> M[Content Loader]
    L --> N[Text Processor]
    L --> O[Embedding Generator]
    L --> P[LanceDB Vector Store]

    M --> Q[Blog Markdown Files]
    N --> R[Text Chunks]
    O --> S[Vector Embeddings]
    P --> T[Semantic Search Results]

    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff9c4
    style F fill:#fff3e0
    style G fill:#e8f5e8
    style L fill:#fce4ec
    style P fill:#e8f5e8
```

## Development Setup

### Prerequisites

- Python 3.11+
- uv package manager
- Google Cloud CLI (for Vertex AI)
- ngrok (for production deployment)

### Project Structure

```
services/ai/
├── src/
│   ├── app/                 # FastAPI chat service
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core functionality
│   │   └── main.py         # FastAPI application
│   ├── agents/             # AI model agents
│   └── indexing/           # Content indexing pipeline
│       ├── main.py         # CLI entry point
│       ├── builder.py      # Main pipeline orchestrator
│       ├── loader.py       # Markdown content loader
│       ├── embedder.py     # Vector embedding generator
│       ├── database.py     # LanceDB vector store
│       └── README.md       # Detailed indexing docs
├── data/
│   ├── content/            # Blog markdown files
│   └── lancedb/           # Vector database
├── scripts/               # Deployment scripts
└── CLI_USAGE.md          # CLI documentation
```

### Installation

1. **Clone and setup environment**:

```bash
git clone <repository-url>
cd services/ai

# Create virtual environment and install dependencies
uv venv
uv sync

# Install the package in editable mode (enables index-cli command)
uv pip install -e .
```

2. **Verify installation**:

```bash
# Test that the CLI is properly installed
index-cli --help

# Test the indexing pipeline
index-cli test
```

This installs all dependencies including:

- **Chat Service**: FastAPI, Google ADK, session management
- **Indexing Pipeline**: sentence-transformers, LanceDB, typer, rich
- **CLI Tools**: Modern `index-cli` command with beautiful output

2. **Configure environment**:

```bash
cp .env.example .env
# Edit .env with your configuration (see Configuration section)
```

3. **Set up Google Cloud authentication**:

```bash
gcloud auth application-default login
```

### Configuration

Update your `.env` file with the following settings:

#### Required Settings

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8081
ENVIRONMENT=development

# Google Cloud Settings (for Gemini models)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_API_KEY=your-google-api-key

# Model Configuration
MODEL_PROVIDER=gemini  # or 'ollama' for local models

# Ollama Settings (when MODEL_PROVIDER=ollama)
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=mistral-small3.1
OLLAMA_MODEL_PRO=llama3.2

# Authentication
AUTH_SECRET=your-super-secret-key

# Frontend URL for CORS
FRONTEND_URL=http://localhost:3000
```

#### CORS Configuration

For production deployments, update `FRONTEND_URL` to include your production domain:

```bash
FRONTEND_URL=https://fromfirstprinciple.com,http://localhost:3000
```

For ngrok integration (see Ngrok Setup section):

```bash
FRONTEND_URL=https://your-ngrok-url.ngrok-free.app,https://fromfirstprinciple.com,http://localhost:3000
```

## Ollama Model Integration

The AI service supports both Gemini and Ollama models through a configurable provider system. You can switch between providers using environment variables for local, private AI processing.

### Ollama Prerequisites

1. **Install Ollama**: Download and install Ollama from [https://ollama.ai](https://ollama.ai)

2. **Start Ollama Server**:

   ```bash
   ollama serve
   ```

3. **Download Models**: Download the models you want to use:

   ```bash
   # Download recommended models with tool support
   ollama pull mistral-small3.1
   ollama pull llama3.2

   # Verify tool support
   ollama show mistral-small3.1
   ```

### Ollama Configuration

Add these settings to your `.env` file:

```bash
# Model provider: 'gemini' or 'ollama'
MODEL_PROVIDER=ollama

# Ollama configuration (used when MODEL_PROVIDER=ollama)
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL=mistral-small3.1
OLLAMA_MODEL_PRO=llama3.2
```

### Available Models

#### Gemini Models (provider: gemini)

- `gemini-2.5-flash`: Fast model for quick responses
- `gemini-2.5-pro`: Advanced model for complex reasoning

#### Ollama Models (provider: ollama)

- `mistral-small3.1`: Mistral Small with tool support
- `llama3.2`: Meta Llama 3.2 with tool support

### Model Selection

The system automatically selects models based on the provider:

- **Default Model**: Used for standard operations

  - Gemini: `gemini-2.5-flash`
  - Ollama: `mistral-small3.1`

- **Pro Model**: Used for complex reasoning (agents use this)
  - Gemini: `gemini-2.5-pro`
  - Ollama: `llama3.2`

### Switching Between Providers

To use Gemini models:

```bash
MODEL_PROVIDER=gemini
```

To use Ollama models:

```bash
MODEL_PROVIDER=ollama
```

After changing the provider, restart the service:

```bash
./scripts/deploy-server.sh restart
```

### Testing Ollama Integration

Run the integration test to verify everything works:

```bash
python test_ollama_integration.py
```

### Ollama Troubleshooting

#### Common Issues

1. **"Failed to create Ollama model"**

   - Ensure Ollama is running: `ollama serve`
   - Check the model is available: `ollama list`
   - Verify API base URL: `curl http://localhost:11434/api/tags`

2. **Tool calling issues**
   - Verify the model supports tools: `ollama show <model-name>`
   - Use models specifically designed for tool use

#### Model Recommendations

For reliable tool support with Ollama:

- **Mistral Small 3.1**: Excellent tool support, good performance
- **Llama 3.2**: Good balance of capabilities and tool support

#### Performance Notes

- Ollama models run locally, providing privacy but requiring local resources
- First requests might be slower as models load into memory
- Consider model size vs. available RAM when choosing models

### Running the Service

#### Development Mode

```bash
./scripts/deploy-server.sh start --dev
```

#### Production Mode

```bash
./scripts/deploy-server.sh start --port 8080
```

The service will be available at:

- **API Documentation**: `http://localhost:8080/docs`
- **Health Check**: `http://localhost:8080/api/v1/health`
- **Chat Endpoint**: `http://localhost:8080/api/v1/root_agent/`

## Ngrok Integration

For exposing your local AI service to the internet (useful for production frontend testing):

### Setup Steps

1. **Start the AI service**:

```bash
./scripts/deploy-server.sh start --port 8080
```

2. **Start ngrok tunnel**:

```bash
ngrok http 8080
```

3. **Update CORS configuration**:

```bash
# In .env file
FRONTEND_URL=https://abc123.ngrok-free.app,https://fromfirstprinciple.com,http://localhost:3000
```

4. **Restart the service**:

```bash
./scripts/deploy-server.sh restart --port 8080
```

5. **Update frontend configuration**:

```bash
# In frontend .env.local
NEXT_PUBLIC_API_BASE_URL=https://abc123.ngrok-free.app
```

### Testing Ngrok Setup

```bash
./tests/test_ngrok_setup.sh
```

### Frontend Integration Script

Use the utility script to easily switch between local and ngrok configurations:

```bash
cd ../frontend
./scripts/switch-api-config.sh ngrok   # Switch to ngrok
./scripts/switch-api-config.sh local   # Switch to local
```

## API Endpoints

### Chat Endpoint

```http
POST /api/v1/root_agent/
Content-Type: application/json

{
  "text": "Your message here",
  "model": "gemini-2.5-flash"  // optional
}
```

Response:

```json
{
  "response": "AI response",
  "references": {},
  "session_id": "uuid",
  "model": "gemini-2.5-flash",
  "confidence": null
}
```

### Available Models

```http
GET /api/v1/root_agent/models
```

### Programmatic Model Usage

```python
from agents.model_factory import create_model, get_default_model, get_pro_model

# Create specific models
gemini_model = create_model('gemini-2.5-flash')
ollama_model = create_model('mistral-small3.1')

# Get models based on current provider
default_model = get_default_model()
pro_model = get_pro_model()
```

### Health Check

```http
GET /api/v1/health
```

## Session Management

The service uses Google ADK for session management, providing:

- **Persistent conversations**: Chat history maintained across requests
- **Session isolation**: Each session has its own conversation context
- **Automatic session creation**: New sessions created as needed
- **Memory management**: Efficient in-memory session storage

## Security

- **CORS Protection**: Configured to only allow requests from specified origins
- **Session validation**: Secure session ID generation and validation
- **Environment isolation**: Sensitive configuration in environment variables
- **Input validation**: Request validation using Pydantic models

## Deployment

### Production Deployment

```bash
./scripts/deploy-server.sh start
```

### Service Management

```bash
# Check status
./scripts/deploy-server.sh status

# Stop service
./scripts/deploy-server.sh stop

# Restart service
./scripts/deploy-server.sh restart

# View logs
tail -f logs/access.log
tail -f logs/error.log
```

## Troubleshooting

### Common Issues

#### CORS Errors

- Ensure frontend domain is in `FRONTEND_URL`
- Restart service after updating environment
- Check browser developer tools for specific CORS errors

#### Connection Issues

- Verify service is running: `curl http://localhost:8080/api/v1/health`
- Check logs: `tail -f logs/error.log`
- Ensure port is not in use: `lsof -i :8080`

#### Ngrok Issues

- Verify tunnel is active: `curl http://127.0.0.1:4040/api/tunnels`
- Test local service first before testing ngrok
- Monitor ngrok connections at: `http://127.0.0.1:4040`

### Logs

Service logs are available in the `logs/` directory:

- `access.log`: HTTP request logs
- `error.log`: Error and debug logs

4. **Quick Start**:

```bash
# Test the indexing pipeline
index-cli test

# Start the chat API service
./scripts/deploy-server.sh start --dev

# Index your blog content
index-cli index

# Search indexed content
index-cli search "machine learning strategy"
```

## Content Indexing CLI

The AI service includes a modern command-line interface for indexing and searching blog content using semantic embeddings.

### Quick Start

```bash
# Test the indexing pipeline
index-cli test

# Index all content
index-cli index

# Search content
index-cli search "machine learning strategy"

# View statistics
index-cli stats
```

### Installation

The CLI is automatically available after installing project dependencies:

```bash
pip install -e .
```

### Available Commands

- **`index-cli test`** - Test pipeline configuration and dependencies
- **`index-cli index`** - Index blog content with optional category filtering
- **`index-cli search`** - Semantic search with similarity scoring
- **`index-cli stats`** - Show indexing statistics and database info
- **`index-cli clear`** - Clear index data with confirmation prompts
- **`index-cli config`** - Display current configuration settings

### Features

- 🎨 **Beautiful Output**: Rich terminal formatting with colors, tables, and progress bars
- 🔍 **Smart Search**: Semantic similarity search using sentence transformers
- ⚡ **Performance**: Efficient vector database with LanceDB and intelligent caching
- 🛠 **Developer Friendly**: Comprehensive error handling and detailed statistics

### Examples

```bash
# Complete workflow
index-cli test
index-cli index
index-cli search "productivity and learning"

# Category-specific operations
index-cli index --category blog
index-cli search "parallel computing" --category engineering

# Development workflow
index-cli index --category blog --slug abstraction
index-cli clear --category blog --yes
```

For detailed usage information, see [CLI_USAGE.md](CLI_USAGE.md).

## Indexing Package (`src/indexing/`)

The indexing package provides a complete semantic search solution with dual search modes (semantic AI similarity and keyword text matching), modern CLI tooling, and high-performance vector storage.

### Quick Overview

```bash
# Test your setup
index-cli test

# Index all blog content
index-cli index

# Semantic search (AI-powered)
index-cli search "machine learning concepts"

# Keyword search (text matching)
index-cli search "exact phrase" --mode keyword

# View system statistics
index-cli stats
```

### Architecture Highlights

- **🧠 Semantic Search**: AI embeddings with vector similarity for conceptual matching
- **🔤 Keyword Search**: Traditional text search with frequency scoring and term matching
- **⚡ High Performance**: LanceDB vector database with GPU acceleration
- **🎨 Modern CLI**: Rich terminal interface with progress bars and colored output
- **📊 Smart Processing**: Intelligent chunking, metadata extraction, and batch operations

### Use Cases

- **Content Discovery**: Help users find relevant blog posts by meaning
- **Research Assistant**: Semantic search for writing and research workflows
- **SEO Enhancement**: Better content organization and related post suggestions
- **Developer Tools**: API integration for building custom search experiences

📖 **For complete technical documentation, process flow diagrams, search mode comparisons, and API reference**, see the [**Indexing System Documentation**](src/indexing/README.md).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Copyright 2025 Loïc Muhirwa

Licensed under the Apache License, Version 2.0
