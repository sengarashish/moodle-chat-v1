# Architecture Documentation

Detailed architecture of the Moodle AI Assistant with RAG system.

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Moodle Platform                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              Local Plugin: AI Assistant                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │ │
│  │  │   Index.php  │  │  API.php     │  │ Document Mgmt   │  │ │
│  │  │  (Chat UI)   │  │ (Endpoints)  │  │ (manage_docs)   │  │ │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘  │ │
│  │         │                  │                    │            │ │
│  │  ┌──────▼──────────────────▼────────────────────▼────────┐  │ │
│  │  │         JavaScript (AMD Modules)                      │  │ │
│  │  │    chat.js          documents.js                      │  │ │
│  │  └─────────────────────────┬──────────────────────────────┘  │ │
│  └────────────────────────────┼─────────────────────────────────┘ │
└────────────────────────────────┼───────────────────────────────────┘
                                 │ HTTP/JSON
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Python Backend (FastAPI)                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    API Layer                                │ │
│  │  /api/chat    /api/ingest/*    /api/health                │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
│  ┌──────────────────────▼─────────────────────────────────────┐ │
│  │              Agent Service (LangGraph)                      │ │
│  │  ┌──────────────────────────────────────────────────────┐  │ │
│  │  │  Query Routing Logic                                  │  │ │
│  │  │  ┌─────────┐  ┌──────────┐  ┌─────────────┐        │  │ │
│  │  │  │   RAG   │  │ Web      │  │  Direct LLM │        │  │ │
│  │  │  │  Route  │  │  Search  │  │   Route     │        │  │ │
│  │  │  └─────────┘  └──────────┘  └─────────────┘        │  │ │
│  │  └──────────────────────────────────────────────────────┘  │ │
│  └──────┬─────────────────┬─────────────────────┬────────────┘ │
│         │                 │                     │                │
│  ┌──────▼──────┐  ┌───────▼────────┐  ┌────────▼────────────┐  │
│  │   Vector    │  │     Search     │  │    LLM Service      │  │
│  │   Store     │  │    Service     │  │  (OpenAI/Anthropic) │  │
│  │   Service   │  │   (Serper/DDG) │  │                     │  │
│  └──────┬──────┘  └────────────────┘  └─────────────────────┘  │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│   Qdrant Vector DB      │
│   (Embeddings Storage)  │
└─────────────────────────┘
```

## Component Details

### 1. Moodle Plugin (PHP)

**Location**: `/local/aiassistant/`

#### Key Files:

- **version.php**: Plugin metadata and version info
- **settings.php**: Admin configuration interface
- **db/install.xml**: Database schema
- **db/access.php**: Capability definitions
- **lang/en/**: Language strings

#### PHP Classes:

```
classes/
├── user_settings.php      # User preference management
├── chat_manager.php       # Chat history CRUD operations
├── document_manager.php   # Knowledge base document tracking
└── api_client.php        # HTTP client for backend communication
```

#### Pages:

- **index.php**: Main chat interface
- **manage_documents.php**: Knowledge base management
- **api.php**: AJAX endpoints for frontend

### 2. Frontend (JavaScript/CSS)

**Location**: `/amd/src/` and `/styles/`

#### JavaScript Modules (AMD):

```javascript
// chat.js - Main chat interface
define(['jquery', 'core/ajax'], function($, Ajax) {
    return {
        init: function(config) {
            // Initialize chat UI
            // Handle message sending
            // Update chat history
        }
    };
});

// documents.js - Document management
define(['jquery'], function($) {
    return {
        init: function(config) {
            // Handle PDF uploads
            // Handle URL submissions
        }
    };
});
```

#### CSS Structure:

```
styles/
├── main.css              # Base styles
└── themes/
    ├── jungle.css        # Jungle theme
    ├── ocean.css         # Ocean theme
    └── space.css         # Space theme
```

### 3. Python Backend (FastAPI)

**Location**: `/backend/`

#### Application Structure:

```
backend/
├── app/
│   ├── main.py                    # FastAPI application entry
│   ├── config.py                  # Configuration management
│   ├── api/                       # API endpoints
│   │   ├── chat.py               # Chat endpoints
│   │   ├── ingest.py             # Ingestion endpoints
│   │   └── health.py             # Health check endpoints
│   └── services/                  # Business logic
│       ├── agent_service.py      # LangGraph agent
│       ├── llm_service.py        # LLM interaction
│       ├── vector_store.py       # Qdrant operations
│       ├── document_service.py   # Document processing
│       └── search_service.py     # Web search
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker image definition
└── .env                          # Environment configuration
```

### 4. Agent Service (LangGraph)

The core intelligence of the system using LangGraph for query routing.

#### State Machine:

```python
class AgentState(TypedDict):
    query: str                          # User query
    history: List[Dict[str, str]]       # Chat history
    user_age: Optional[int]             # For age customization
    rag_results: Optional[List[Dict]]   # RAG search results
    search_results: Optional[List[Dict]] # Web search results
    route: Optional[str]                # Chosen route
    response: Optional[str]             # Final response
    sources: Optional[List[str]]        # Source citations
```

#### Workflow:

```
Start
  ↓
Route Query (LLM Classification)
  ├─→ "knowledge_base" → Retrieve from RAG
  ├─→ "current_events" → Search Web
  └─→ "general" → Direct LLM
       ↓
Generate Response (with context)
  ↓
End
```

#### Query Classification:

The agent uses the LLM itself to classify queries:

```python
async def _route_query(self, state: AgentState):
    classification_prompt = """
    Classify this query:
    1. knowledge_base - Course materials, documents
    2. current_events - Recent events, news
    3. general - General questions

    Query: {query}
    """
    classification = await llm.generate(classification_prompt)
    state["route"] = parse_classification(classification)
    return state
```

### 5. RAG System

#### Vector Store (Qdrant):

- **Collection**: `moodle_knowledge`
- **Vector Size**: 1536 (OpenAI text-embedding-3-small)
- **Distance Metric**: Cosine similarity
- **Indexing**: HNSW algorithm

#### Document Processing Pipeline:

```
Input Document (PDF/URL)
  ↓
Text Extraction
  ↓
Chunking (RecursiveCharacterTextSplitter)
  - chunk_size: 1000
  - chunk_overlap: 200
  ↓
Generate Embeddings (OpenAI)
  ↓
Store in Qdrant with Metadata
  - document_id
  - source
  - page/section
  - type
```

#### Search Process:

```
User Query
  ↓
Generate Query Embedding
  ↓
Semantic Search in Qdrant
  - top_k: 5
  - score_threshold: 0.7
  ↓
Return Relevant Chunks
```

### 6. LLM Integration

#### Supported Providers:

**OpenAI**:
- Model: GPT-4 Turbo Preview
- Embedding: text-embedding-3-small
- Features: Function calling, streaming

**Anthropic**:
- Model: Claude 3 Opus
- Features: Long context, constitutional AI

#### Age-Based Customization:

```python
def get_system_prompt(user_age):
    if user_age <= 12:
        return child_prompt  # Simple language, encouraging
    elif user_age <= 17:
        return teen_prompt   # Clear, relatable examples
    else:
        return adult_prompt  # Professional, detailed
```

### 7. Web Search Integration

#### Providers:

1. **Serper** (Primary): Google search API
2. **DuckDuckGo** (Fallback): Free search

#### Search Flow:

```
Current Event Query
  ↓
Execute Web Search (top 5 results)
  ↓
Extract: title, snippet, URL
  ↓
Format as Context
  ↓
Generate Response with LLM
```

## Data Flow

### Chat Message Flow:

```
1. User types message in Moodle UI
   ↓
2. JavaScript sends POST to api.php
   ↓
3. PHP validates session & capabilities
   ↓
4. PHP sends POST to Python backend
   ↓
5. Agent Service processes:
   a. Route query
   b. Retrieve context (RAG/Search)
   c. Generate response
   ↓
6. Response sent back to PHP
   ↓
7. PHP saves to database
   ↓
8. JavaScript renders in UI
```

### Document Ingestion Flow:

```
1. Admin uploads PDF in manage_documents.php
   ↓
2. File saved to server
   ↓
3. Record created in database (status: pending)
   ↓
4. File sent to backend /api/ingest/pdf
   ↓
5. Backend processes:
   a. Extract text from PDF
   b. Split into chunks
   c. Generate embeddings
   d. Store in Qdrant
   ↓
6. Update database (status: completed, chunks: N)
```

## Database Schema

### Moodle Tables:

```sql
-- Chat sessions
local_aiassistant_chats
  - id, userid, title, theme, timecreated, timemodified

-- Chat messages
local_aiassistant_messages
  - id, chatid, role, content, metadata, timecreated

-- Knowledge base documents
local_aiassistant_documents
  - id, title, sourcetype, sourceurl, filepath, status, chunks, uploaderid, timecreated

-- User settings
local_aiassistant_settings
  - id, userid, name, value, timemodified
```

### Qdrant Structure:

```json
{
  "id": "uuid",
  "vector": [0.123, 0.456, ...],
  "payload": {
    "text": "chunk content",
    "metadata": {
      "source": "document.pdf",
      "page": 1,
      "type": "pdf",
      "document_id": 123
    }
  }
}
```

## Security

### Authentication Flow:

```
User Request
  ↓
Moodle Session Check
  ↓
Capability Verification
  ↓
SESSKEY Validation
  ↓
Backend API Call (internal)
```

### API Security:

- No public backend exposure (internal network only)
- Moodle session validation required
- Capability-based access control
- API key stored server-side only

## Performance Considerations

### Caching Strategy:

- **Moodle**: Built-in cache for settings
- **Backend**: No caching (stateless)
- **Qdrant**: Built-in HNSW index caching

### Optimization Points:

1. **Vector Search**:
   - Adjust `top_k` and `score_threshold`
   - Use filters to narrow search space

2. **LLM Calls**:
   - Limit chat history length
   - Use streaming for better UX
   - Consider caching common queries

3. **Document Processing**:
   - Process asynchronously
   - Queue large uploads
   - Batch embeddings generation

## Scalability

### Horizontal Scaling:

```
                Load Balancer
                      ↓
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   Backend 1     Backend 2     Backend 3
        └─────────────┼─────────────┘
                      ↓
              Qdrant Cluster
```

### Vertical Scaling:

- Increase Qdrant memory for larger collections
- More CPU for embedding generation
- Adjust chunk sizes for memory/accuracy tradeoff

## Monitoring

### Health Checks:

- `/api/health`: Basic health
- `/api/health/detailed`: Full service status

### Metrics to Monitor:

- Response time
- Error rate
- Token usage (LLM)
- Vector store size
- Memory usage
- CPU usage

### Logging:

- Backend: Loguru with structured logging
- Moodle: Standard Moodle debugging
- Docker: Container logs

## Extension Points

### Adding New Features:

1. **New Document Types**:
   - Add loader in `document_service.py`
   - Update API endpoints
   - Modify UI

2. **New LLM Providers**:
   - Extend `llm_service.py`
   - Add configuration
   - Update settings

3. **New Search Providers**:
   - Extend `search_service.py`
   - Add API key configuration

4. **New Themes**:
   - Add CSS file
   - Register in language strings
   - Update selector

## Troubleshooting Guide

### Common Issues:

1. **Connection Errors**: Check Docker containers, firewall
2. **Slow Responses**: Check LLM API, vector search performance
3. **Ingestion Failures**: Verify file format, API keys
4. **Empty Responses**: Check LLM API credits, error logs

See INSTALLATION.md for detailed troubleshooting.
