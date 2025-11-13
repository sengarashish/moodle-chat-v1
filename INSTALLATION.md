# Installation Guide

Complete installation guide for the Moodle AI Assistant with RAG.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Setup](#backend-setup)
3. [Moodle Plugin Installation](#moodle-plugin-installation)
4. [Configuration](#configuration)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Moodle**: Version 4.0 or higher
- **PHP**: Version 7.4 or higher
- **Python**: Version 3.11 or higher
- **Docker**: Version 20.10 or higher
- **Docker Compose**: Version 2.0 or higher

### API Keys

You'll need at least one of the following:

- **OpenAI API Key**: Get from [platform.openai.com](https://platform.openai.com/api-keys)
- **Anthropic API Key**: Get from [console.anthropic.com](https://console.anthropic.com/)

Optional:
- **Serper API Key**: For enhanced web search ([serper.dev](https://serper.dev))

## Backend Setup

### 1. Clone the Repository

For development in your Moodle local plugins directory:

```bash
cd /path/to/moodle/local/
git clone <repository-url> aiassistant
cd aiassistant
```

### 2. Configure Environment Variables

```bash
cd backend
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Choose your LLM provider
LLM_PROVIDER=openai  # or anthropic

# Add your API key(s)
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Optional: For web search
SERPER_API_KEY=your-key-here

# Other settings (defaults are usually fine)
QDRANT_HOST=qdrant
QDRANT_PORT=6333
BACKEND_PORT=8000
```

### 3. Start Backend Services

Using Docker Compose (recommended):

```bash
# From the plugin root directory
docker-compose up -d
```

This will start:
- Qdrant vector database on port 6333
- FastAPI backend on port 8000

Verify services are running:

```bash
docker-compose ps
curl http://localhost:8000/api/health
```

### 4. Manual Setup (Alternative)

If you prefer not to use Docker:

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start Qdrant separately (requires Docker or binary)
docker run -p 6333:6333 qdrant/qdrant

# Start backend
uvicorn app.main:app --reload
```

## Moodle Plugin Installation

### 1. Plugin Files

If you cloned into `moodle/local/aiassistant`, the files are already in place.

Otherwise, copy the plugin files:

```bash
cp -r <plugin-directory> /path/to/moodle/local/aiassistant
```

### 2. Set Permissions

```bash
cd /path/to/moodle/local/aiassistant
chmod -R 755 .
chown -R www-data:www-data .  # Adjust user/group as needed
```

### 3. Install Plugin

1. Log in to Moodle as administrator
2. Navigate to: **Site Administration > Notifications**
3. Moodle will detect the new plugin
4. Click **Upgrade Moodle database now**
5. Follow the installation prompts

### 4. Verify Installation

Check that the plugin appears in:
- **Site Administration > Plugins > Local plugins > AI Assistant**

## Configuration

### 1. Plugin Settings

Navigate to: **Site Administration > Plugins > Local plugins > AI Assistant**

Configure:

1. **LLM Provider**: Choose OpenAI or Anthropic
2. **API Keys**: Enter your API key(s)
3. **Backend URL**: `http://localhost:8000` (or your backend URL)
4. **Default Theme**: Choose default chat theme
5. **Age-Based Responses**: Enable/disable age customization
6. **Serper API Key**: (Optional) For web search

Click **Save changes**

### 2. Permissions

Set up capabilities for different user roles:

Navigate to: **Site Administration > Users > Permissions > Define roles**

For each role, configure:

- `local/aiassistant:use` - Allow users to use the AI assistant
- `local/aiassistant:managecontent` - Allow managing knowledge base
- `local/aiassistant:viewallhistory` - Allow viewing all users' history

Recommended defaults:
- **Students**: `use`
- **Teachers**: `use`, `managecontent`
- **Managers**: All capabilities

### 3. Add to Navigation

The AI Assistant will automatically appear in the Moodle navigation menu.

To customize the menu placement, edit the plugin's `lib.php` file.

## Testing

### 1. Test Backend

```bash
# Health check
curl http://localhost:8000/api/health

# Detailed health check
curl http://localhost:8000/api/health/detailed

# Test chat (requires API key to be configured)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### 2. Test Moodle Interface

1. Log in as a user with `local/aiassistant:use` capability
2. Navigate to **AI Assistant** from the main menu
3. Try sending a message
4. Test theme switching

### 3. Test Knowledge Base

1. Log in as administrator or teacher
2. Go to: **Site Administration > AI Assistant > Knowledge Base**
3. Upload a test PDF or add a URL
4. Wait for processing to complete
5. Ask a question related to the uploaded content

### 4. Verify RAG System

Check that documents are being indexed:

```bash
# Check Qdrant collection
curl http://localhost:6333/collections/moodle_knowledge

# Check collection statistics
curl http://localhost:8000/api/health/detailed
```

## Troubleshooting

### Backend Not Connecting

**Symptoms**: "Could not connect to AI service" error

**Solutions**:
1. Verify backend is running: `docker-compose ps`
2. Check backend logs: `docker-compose logs backend`
3. Verify Backend URL in Moodle settings
4. Check firewall rules (port 8000)

### Qdrant Connection Issues

**Symptoms**: "Failed to initialize vector store"

**Solutions**:
1. Check Qdrant is running: `curl http://localhost:6333/health`
2. View logs: `docker-compose logs qdrant`
3. Restart services: `docker-compose restart`

### Document Ingestion Fails

**Symptoms**: Documents stuck in "processing" status

**Solutions**:
1. Check backend logs for errors
2. Verify PDF is valid and not corrupted
3. Check file permissions
4. Ensure sufficient disk space
5. Verify API keys are correct

### Chat Responses Not Working

**Symptoms**: Empty responses or errors

**Solutions**:
1. Verify API keys are correct and have credits
2. Check backend logs: `docker-compose logs backend`
3. Test API directly: `curl http://localhost:8000/api/health/detailed`
4. Check LLM provider status

### Age-Based Responses Not Working

**Symptoms**: All responses are the same regardless of age

**Solutions**:
1. Enable in plugin settings
2. Ensure user profiles have age field populated
3. Check that custom profile field is named 'age'

### Theme Not Loading

**Symptoms**: Theme selector doesn't work

**Solutions**:
1. Clear Moodle caches: **Site Administration > Development > Purge all caches**
2. Check browser console for JavaScript errors
3. Verify CSS files are accessible

## Advanced Configuration

### Production Deployment

For production deployment:

1. **Use environment-specific settings**:
   - Set `DEBUG=false` in `.env`
   - Use production-grade database for Moodle
   - Consider managed Qdrant instance

2. **Security**:
   - Use HTTPS for all connections
   - Set up proper CORS policies
   - Restrict backend access with firewall rules
   - Use strong API keys and rotate regularly

3. **Performance**:
   - Increase Qdrant resources for large knowledge bases
   - Configure rate limiting
   - Use CDN for static assets
   - Monitor response times

4. **Backup**:
   - Backup Qdrant data: `docker-compose exec qdrant /bin/bash`
   - Backup Moodle database regularly
   - Store API keys securely (e.g., secrets manager)

### Scaling

For high-traffic deployments:

1. **Horizontal Scaling**:
   - Run multiple backend instances behind load balancer
   - Use managed Qdrant or cluster setup
   - Consider Redis for caching

2. **Vertical Scaling**:
   - Increase Docker container resources
   - Optimize chunk size and overlap
   - Adjust top_k and score_threshold

## Support

For issues and questions:

- **GitHub Issues**: <repository-url>/issues
- **Moodle Forums**: https://moodle.org/plugins/local_aiassistant
- **Documentation**: See README.md

## Next Steps

After successful installation:

1. [Upload initial knowledge base documents](#testing)
2. Configure user permissions
3. Customize themes (optional)
4. Set up monitoring and logging
5. Train users on how to use the assistant

## Updating

To update the plugin:

```bash
cd /path/to/moodle/local/aiassistant
git pull origin main
docker-compose down
docker-compose up -d --build
```

Then visit **Site Administration > Notifications** to apply any database updates.
