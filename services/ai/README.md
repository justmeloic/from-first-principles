# From First Principles - AI Service

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Google ADK](https://img.shields.io/badge/Google_ADK-1.5.0+-4285F4.svg)
![GCP](https://img.shields.io/badge/Google_Cloud-4285F4?logo=google-cloud&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-Local_AI-00B4D8?logo=ollama&logoColor=white)

AI backend service for the From First Principles platform, providing intelligent chat capabilities powered by Google's Gemini models and local Ollama models.

## Overview

This service provides a FastAPI-based backend that powers the AI chat functionality for the From First Principles website. It features:

- **Multi-Model Support**: Choose between Google Gemini models or local Ollama models
- **Session Management**: Persistent conversation history across multiple interactions
- **CORS Configuration**: Secure cross-origin requests from the frontend
- **Static File Serving**: Integrated frontend serving capabilities
- **Production Ready**: Deployment scripts and production configurations

## Architecture

```mermaid
graph TD
    A[Frontend - fromfirstprinciple.com] --> B[AI Service API]
    B --> C[Google ADK Session Management]
    B --> D{Model Provider}
    C --> E[In-Memory Session Store]
    D --> F[Gemini Models]
    D --> G[Ollama Models]
    F --> H[Vertex AI / Google AI Studio]
    G --> I[Local Ollama Server]

    style A fill:#e3f2fd
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff9c4
    style F fill:#fff3e0
    style G fill:#e8f5e8
```

## Development Setup

### Prerequisites

- Python 3.11+
- uv package manager
- Google Cloud CLI (for Vertex AI)
- ngrok (for production deployment)

### Installation

1. **Install dependencies**:

```bash
uv venv
uv sync
```

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

Copyright 2025 Loïc Muhirwa

Licensed under the Apache License, Version 2.0
