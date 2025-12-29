# 🤖 Multi-Agent AI Assistant with Supervisor Orchestration

A powerful **multi-modal AI assistant** powered by **Supervisor Agent Architecture**, specialized domain agents, and advanced tools for research, finance, travel, shopping, jobs, and recipes.

## 🌟 Evolution: From Single Agent to Multi-Agent System

Previously: Basic mem0 + Anam avatar with single LLM

**Now:** Full supervisor-orchestrated multi-agent system with:
- ✅ Specialized agents for 6 different domains
- ✅ Intelligent routing based on user intent
- ✅ Parallel processing capabilities
- ✅ Long-term memory with Mem0
- ✅ Multi-modal interactions (text)

## 📊 Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit Frontend                     │
│                       (Text Chat)                         │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│                 FastAPI Backend                           │
│         /multi-agent/stream Endpoint                     │
└──────────────────┬───────────────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────────────┐
│           SUPERVISOR AGENT (LangGraph)                   │
│   • Intent Classification                                 │
│   • Domain Routing                                        │
│   • Context Management                                    │
└──────────────────┬───────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬────────────┐
    │              │              │            │
    ▼              ▼              ▼            ▼
┌────────┐   ┌──────────┐   ┌────────┐   ┌─────────┐
│Research│   │ Finance  │   │Travel  │   │Shopping │
│ Agent  │   │  Agent   │   │ Agent  │   │ Agent   │
└───┬────┘   └──────────┘   └────────┘   └─────────┘
    │
┌───▼────┐   ┌──────────┐
│  Jobs  │   │ Recipes  │
│ Agent  │   │  Agent   │
└────────┘   └──────────┘

        │
        ├─ Tools & Services ─┐
        │                    │
    ┌───▼───────────────────▼──────────────┐
    │  SerpApi  │  Mem0 │ ChromaDB │ Groq  │
    └──────────────────────────────────────┘
        │
    ┌───▼───────────────────────────────────┐
    │  External APIs & Knowledge Bases      │
    │  • Google Search/Jobs/Flights/Recipes│
    │  • Zep Knowledge Graph                │
    │  • Vector Database                    │
    │  • LLM Providers                      │
    └───────────────────────────────────────┘
```

## 🎯 Specialized Agents

| Agent | Purpose | Tools |
|-------|---------|-------|
| 🔍 **Research** | Web research, articles, information gathering | News search, ChromaDB RAG, document retrieval |
| 💰 **Finance** | Financial info, stocks, investment advice | Financial news, market data, guidance |
| ✈️ **Travel** | Flights, hotels, trip planning | Flight search, hotel booking, guides |
| 🛍️ **Shopping** | Product recommendations | Product search, price comparison |
| 💼 **Jobs** | Job search, career advice | Google Jobs, resume tips, guidance |
| 👨🍳 **Recipes** | Recipe discovery with ratings | Recipe search, ingredients, cooking tips |

## 🚀 Key Features

### Multi-Modal Interactions
- **🗣️ Unified Voice & Chat** - Semantic voice interaction with auto-summarization
- **📝 Smart Summaries** - Tabbed view with concise spoken summaries and full detail

### Advanced Capabilities
- **🧠 Long-term Memory** - Mem0 integration (never forgets)
- **📚 Retrieval-Augmented Generation** - ChromaDB + Groq for multi-PDF context
- **🔗 Knowledge Graph** - Zep Cloud for structured entity relationships
- **⚡ Parallel Processing** - Concurrent agent execution
- **🤖 Intelligent Routing** - Automatic domain classification

### Tech Stack
| Component | Technology |
|-----------|-----------|
| **Agent Orchestration** | LangGraph with Supervisor pattern |
| **LLM** | Groq (Llama 3.1 / Mixtral) |
| **Memory** | Mem0 (persistent, never forgets) |
| **Vector DB** | ChromaDB for RAG |
| **Web Tools** | SerpApi for search/jobs/flights/recipes |
| **Knowledge Graph** | Zep Cloud |
| **Backend** | FastAPI with streaming |
| **Frontend** | Streamlit |

## 📦 Installation

### Prerequisites
- Python 3.12+
- UV package manager

### Install Dependencies

```bash
uv sync
```

### Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

**Required API Keys:**
- `GROQ_API` - [Get from Groq](https://console.groq.com/) - Primary Intelligence & Voice Provider
- `SERPAPI_KEY` - [Get from SerpApi](https://serpapi.com/)
- `MEM0_API_KEY` - [Get from Mem0](https://mem0.ai/)

## 🎮 Running the Application

### 1. Ingest Data (Optional)

Populate the knowledge graph with your data:

```bash
python scripts/ingest_to_graph.py
```

### 2. Start Backend Server

```bash
uvicorn backend:app --port 8000 --reload
```

### 3. Start Frontend (in separate terminal)

#### Option A: Multi-Modal Frontend (Recommended)
```bash
streamlit run app_v2.py
```

### 4. Access the Application

- **Streamlit UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health

## 📡 API Endpoints

### Session Management
```
POST /mem0/session
- Create user session in Mem0

Request:
{
  "user_id": "demo-user",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com"
}
```

### Intelligent Routing
```
POST /route
- Get supervisor routing decision

Request:
{
  "user_id": "demo-user",
  "session_id": "session-demo-user",
  "message": "Find me a job as a data scientist",
  "conversation_history": [...]
}

Response:
{
  "recommended_agent": "jobs",
  "classified_domain": "jobs",
  "context": {...}
}
```

### Multi-Agent Streaming
```
POST /multi-agent/stream
- Stream response from appropriate specialized agent

Request:
{
  "user_id": "demo-user",
  "session_id": "session-demo-user",
  "message": "Show me flights to NYC",
  "mode": "text",
  "conversation_history": [...]
}

Returns: Server-Sent Events (SSE) stream
```

### Health Check
```
GET /health
GET /agents
GET /zep/test-graph?q=<query>
```

## 🧠 How Agent Routing Works

1. **User sends message** → "Find me a data scientist job"
2. **Supervisor Agent** analyzes intent using LLM
3. **Domain Classification** → "jobs" domain detected
4. **Route to Specialist** → Jobs Agent selected
5. **Execute Tools** → SerpApi Google Jobs search
6. **Generate Response** → Jobs agent streams response
7. **Save Memory** → Store in Mem0 + Zep for future context

## 💾 Memory Management

### Mem0 Integration
- **Persistent Memory:** Survives across sessions
- **Semantic Search:** Find relevant past interactions
- **User Profile:** Build understanding of preferences

### Zep Cloud Integration  
- **Thread Memory:** Conversation history
- **Knowledge Graph:** Entity relationships
- **User Context:** Automatic context extraction

Example memory usage:
```python
# Add memory
await mem0_service.add_memory(
    user_id="demo-user",
    message="Interested in Python data science roles",
    metadata={"domain": "jobs", "query": "data scientist"}
)

# Retrieve memories
memories = await mem0_service.retrieve_memories(
    user_id="demo-user",
    query="jobs I'm interested in"
)
```

## 📚 Multi-Modal Interaction Examples

### Text Chat
```
User: "What are the best flights to Tokyo?"
→ Routed to Travel Agent
→ Uses SerpApi flight search
→ Returns options with prices
```

## 🔍 Example: Research Agent

```python
# User query
"What are the latest developments in quantum computing?"

# Supervisor routes to Research Agent
# Research Agent:
# 1. Searches recent news via SerpApi
# 2. Queries ChromaDB for relevant documents
# 3. Uses Groq LLM for RAG synthesis
# 4. Streams response to user

# Example response flow:
news_results = await serpapi_service.search_news(
    "quantum computing latest", num_results=5
)

doc_results = await chromadb_service.query_documents(
    "quantum computing breakthroughs"
)

response = await chromadb_service.generate_rag_response(
    query="quantum computing developments",
    context_documents=doc_results
)
```

## 📖 Learn More

- **LangGraph Guide:** https://langchain-ai.github.io/langgraph/
- **LangGraph Guide:** https://langchain-ai.github.io/langgraph/
- **See full demo:** Check `zep_demo.ipynb` for detailed examples

## 🤝 Contributing

Contributions welcome! Feel free to:
- Add new specialized agents for other domains
- Improve routing logic
- Add new tools/integrations
- Enhance memory management
- Submit pull requests

## 📜 License

This project is open source. See LICENSE for details.

## 🎓 Learning Resources

**Multi-Agent Systems:**
- Agent design patterns
- Supervisor/hierarchical architectures
- Tool selection and execution
- Memory management strategies

**Our Stack:**
- LangGraph for orchestration
- Specialized agent patterns
- RAG implementation

---

**Built with ❤️ using LangGraph, Anam AI, and modern AI tools**

