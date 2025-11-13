# Moodle AI Assistant with RAG

A comprehensive AI assistant Moodle module with Retrieval-Augmented Generation (RAG) capabilities.

## Features

- **RAG-Powered Responses**: Uses Qdrant vector database with LangChain for intelligent document retrieval
- **Multi-Source Knowledge**: Ingests PDFs and web URLs (expandable to more sources)
- **Smart Query Routing**: Checks RAG KB first, falls back to LLM, fetches latest data from internet when needed
- **Age-Adaptive Responses**: Customizes language and complexity based on user age
- **Chat History**: Full conversation history similar to OpenAI/Anthropic interfaces
- **Customizable Themes**: Multiple UI themes (jungle, ocean, space) with easy extensibility
- **Moodle Integration**: Seamless integration with Moodle user management and authentication

## Architecture

### Components

1. **Moodle Module** (`local/aiassistant/`): PHP-based frontend and Moodle integration
2. **Python Backend** (`backend/`): FastAPI service with LangChain/LangGraph agents
3. **Qdrant Vector DB**: Vector storage for RAG system
4. **PostgreSQL**: Chat history and configuration storage

### Technology Stack

- **Frontend**: Moodle (PHP), JavaScript, CSS
- **Backend**: Python 3.11+, FastAPI, LangChain, LangGraph
- **Vector DB**: Qdrant
- **Database**: PostgreSQL (Moodle's existing DB)
- **LLM**: OpenAI/Anthropic (configurable)

## Installation

### Prerequisites

- Moodle 4.0 or higher
- Docker and Docker Compose
- Python 3.11+
- PostgreSQL (typically already installed with Moodle)

### Quick Start

1. **Clone the repository**:
```bash
cd /path/to/moodle/local/
git clone <repository-url> aiassistant
```

2. **Set up the Python backend**:
```bash
cd aiassistant/backend
cp .env.example .env
# Edit .env with your API keys and configuration
```

3. **Start services with Docker Compose**:
```bash
docker-compose up -d
```

4. **Install the Moodle plugin**:
- Navigate to Site Administration > Notifications
- Follow the installation prompts
- Configure the plugin settings

5. **Configure API Keys**:
- Go to Site Administration > Plugins > Local plugins > AI Assistant
- Enter your OpenAI/Anthropic API key
- Configure other settings as needed

## Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# LLM Provider (openai or anthropic)
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Qdrant Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=moodle_knowledge

# Search Provider (optional)
SERPER_API_KEY=your-serper-api-key

# Backend Configuration
BACKEND_PORT=8000
MOODLE_BASE_URL=http://localhost
```

### Moodle Plugin Settings

- **LLM Provider**: Choose between OpenAI or Anthropic
- **API Keys**: Configure your LLM API keys
- **Backend URL**: URL of the Python backend service
- **Default Theme**: Default chat UI theme
- **Age-Based Responses**: Enable/disable age-adaptive responses

## Usage

### For Users

1. Navigate to the AI Assistant from the Moodle navigation menu
2. Select your preferred theme (jungle, ocean, space)
3. Start chatting with the AI assistant
4. View your chat history in the sidebar

### For Administrators

#### Adding Documents

1. Go to Site Administration > AI Assistant > Knowledge Base
2. Upload PDF documents or add web URLs
3. Documents are automatically processed and added to the vector database

#### Managing Settings

1. Navigate to Site Administration > Plugins > Local plugins > AI Assistant
2. Configure LLM provider, API keys, and other settings
3. Customize age-based response templates

## API Endpoints

The Python backend exposes the following REST API endpoints:

- `POST /api/chat`: Send a message and get AI response
- `POST /api/ingest/pdf`: Upload and ingest PDF document
- `POST /api/ingest/url`: Ingest content from web URL
- `GET /api/history/{user_id}`: Get chat history for user
- `GET /api/health`: Health check endpoint

## Development

### Running Backend Locally

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Adding New Themes

1. Create CSS file in `local/aiassistant/styles/themes/{theme-name}.css`
2. Add theme configuration in `local/aiassistant/classes/themes.php`
3. Theme will automatically appear in the UI selector

### Adding New Document Sources

1. Create ingestion handler in `backend/app/services/ingest/`
2. Register handler in `backend/app/services/ingest_service.py`
3. Add UI controls in the Moodle admin interface

## Troubleshooting

### Backend Connection Issues

- Verify Docker containers are running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`
- Ensure firewall allows connection to backend port

### Vector Search Not Working

- Verify Qdrant is running: `curl http://localhost:6333/health`
- Check if collection exists: See Qdrant dashboard
- Re-ingest documents if needed

### Chat History Not Saving

- Check Moodle database connection
- Verify table `local_aiassistant_history` exists
- Check Moodle logs for errors

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

## License

GPL v3 (to comply with Moodle licensing)

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Moodle Forums: https://moodle.org/plugins/local_aiassistant

## Roadmap

- [ ] Support for more LLM providers (Llama, Mistral)
- [ ] Voice input/output
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Integration with Moodle gradebook
- [ ] Mobile app support
- [ ] Collaborative chat sessions
