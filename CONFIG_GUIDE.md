# Configuration Guide

## Multi-Agent System Setup

This guide covers all the configuration options and API integrations for the multi-agent AI assistant.

## 📋 Required API Keys

### 1. **Mem0** (Memory & Knowledge Graph)
- **Purpose:** Conversation memory, knowledge graph, entity tracking
- **Get Key:** https://mem0.ai/
- **Setup:**
  ```
  MEM0_API_KEY=your_key_here
  MEM0_ENABLED=true
  ```
- **Cost:** Free tier available
- **Docs:** https://docs.mem0.ai/

### 2. **Cerebras** (LLM - Only Provider)
- **Purpose:** 120B parameter open-source model for all reasoning tasks
- **Get Key:** https://console.cerebras.ai/
- **Setup:**
  ```
  CEREBRAS_API_KEY=your_key_here
  PRIMARY_LLM_MODEL=cerebras/gpt-oss-120b-chat
  ```
- **Cost:** Very affordable inference
- **Docs:** https://docs.cerebras.ai/

### 3. **SerpApi** (Web Search & Tools)
- **Purpose:** Google Jobs, Flights, Hotels, Recipes, News
- **Get Key:** https://serpapi.com/
- **Setup:**
  ```
  SERPAPI_KEY=your_key_here
  ```
- **Cost:** Credit-based pricing
- **Features:**
  - Google Search / News search
  - Google Jobs search
  - Google Flights search
  - Google Hotels search
  - Recipe data
- **Docs:** https://serpapi.com/docs

### 4. **Anam AI** (Avatar & Voice - Optional)
- **Purpose:** Realistic AI avatar with speech-to-speech
- **Get Key:** https://anam.ai/
- **Setup:**
  ```
  ANAM_API_KEY=your_key_here
  ENABLE_VIDEO_AVATAR=true
  ```
- **Cost:** Pay-as-you-go
- **Docs:** https://docs.anam.ai/

### 5. **Groq** (Fast Inference - Optional)
- **Purpose:** Fast LLM inference for RAG synthesis
- **Get Key:** https://console.groq.com/
- **Setup:**
  ```
  GROQ_API_KEY=your_key_here
  ```
- **Cost:** Free tier available
- **Model:** mixtral-8x7b-32768
- **Docs:** https://console.groq.com/docs

## ⚙️ Configuration Options

### Interaction Modes

```env
ENABLE_TEXT_CHAT=true        # Text-based Streamlit interface
ENABLE_VIDEO_AVATAR=true     # Anam AI video avatar
ENABLE_VOICE_AGENT=true      # FastRTC ultra-low latency voice
```

### Memory Configuration

```env
MEM0_ENABLED=true
MEM0_VERSION=v1.0
CHROMADB_COLLECTION_NAME=documents
CHROMADB_PERSIST_DIRECTORY=./data/chroma
```

### Agent Domains

```env
AGENT_DOMAINS=research,finance,travel,shopping,jobs,recipes
```

### FastRTC Configuration (Voice)

```env
FASTRTC_ENABLED=true
FASTRTC_SERVER_URL=http://localhost:8080
```

## 🚀 Quick Start Setup

### Step 1: Create `.env` file

```bash
cp .env.example .env
```

### Step 2: Get API Keys (in order of importance)

1. **Cerebras** - Essential for LLM
   - Go to https://console.cerebras.ai/
   - Sign up and create API key
   - Copy to `CEREBRAS_API_KEY`

2. **SerpApi** - For specialized agent tools
   - Go to https://serpapi.com/
   - Create account
   - Copy to `SERPAPI_KEY`

3. **Mem0** - For long-term memory
   - Go to https://mem0.ai/
   - Create account
   - Copy to `MEM0_API_KEY`

4. **Groq** - Optional, for fast inference
   - Go to https://console.groq.com/
   - Create account
   - Copy to `GROQ_API_KEY`

5. **Anam** - Optional, for video avatar
   - Go to https://anam.ai/
   - Create account
   - Copy to `ANAM_API_KEY`

### Step 3: Fill `.env` file

```bash
# Edit .env and paste your API keys
# At minimum, you need:
# - CEREBRAS_API_KEY or OPENROUTER_API_KEY
# - SERPAPI_KEY (for specialized agents)
```

### Step 4: Install and Run

```bash
# Install dependencies
uv sync

# Start backend
uvicorn backend:app --port 8000 --reload

# In another terminal, start frontend
streamlit run app_v2.py
```

## � Environment Variables Reference

```env
# Core APIs
ANAM_API_KEY=                      # Optional: Anam avatar service
CEREBRAS_API_KEY=                  # REQUIRED: Only LLM provider
SERPAPI_KEY=                       # SerpApi for searches
MEM0_API_KEY=                      # Mem0 persistent memory
GROQ_API_KEY=                      # Optional: Groq fast inference

# Anam Configuration
ANAM_API_BASE_URL=https://api.anam.ai
ANAM_AVATAR_ID=30f...
ANAM_VOICE_ID=6bf...

# Mem0 Configuration
MEM0_ENABLED=true
MEM0_VERSION=v1.0

# ChromaDB Configuration
CHROMADB_COLLECTION_NAME=documents
CHROMADB_PERSIST_DIRECTORY=./data/chroma

# Agent Configuration
PRIMARY_LLM_MODEL=cerebras/gpt-oss-120b-chat
AGENT_DOMAINS=research,finance,travel,shopping,jobs,recipes

# Interaction Modes
ENABLE_TEXT_CHAT=true
ENABLE_VIDEO_AVATAR=true
ENABLE_VOICE_AGENT=true

# FastRTC
FASTRTC_ENABLED=true
FASTRTC_SERVER_URL=http://localhost:8080
```

## 🎯 Agent-Specific Tools

### Research Agent
- **Requires:** `SERPAPI_KEY`, `GROQ_API_KEY`
- **Tools:** News search, ChromaDB RAG, document retrieval
- **Uses:** news search, document embedding, synthesis

### Finance Agent
- **Requires:** `SERPAPI_KEY`, `CEREBRAS_API_KEY`
- **Tools:** Financial news, market data lookup
- **Uses:** news search, financial reasoning

### Travel Agent
- **Requires:** `SERPAPI_KEY`
- **Tools:** Flight search, hotel search
- **Uses:** SerpApi flight/hotel endpoints

### Shopping Agent
- **Requires:** `SERPAPI_KEY`
- **Tools:** Product search, price comparison
- **Uses:** Google search via SerpApi

### Jobs Agent
- **Requires:** `SERPAPI_KEY`
- **Tools:** Google Jobs search, resume tips
- **Uses:** SerpApi jobs endpoint

### Recipes Agent
- **Requires:** `SERPAPI_KEY`
- **Tools:** Recipe discovery with ratings
- **Uses:** SerpApi recipe/local results

## 💰 Cost Estimation

| Service | Free Tier | Est. Monthly (Light Use) |
|---------|-----------|--------------------------|
| Cerebras | Yes (limited) | ~$5-20 |
| SerpApi | No (starts $0.20/req) | ~$10-50 |
| Mem0 | Yes (500 memories/mo) | ~$5-20 |
| Groq | Yes (generous) | ~$0-10 |
| Anam AI | No (pay-per-minute) | ~$20-100 |

**Total Estimate:** $50-270/month for production use

## 🔒 Security Best Practices

1. **Never commit `.env` file**
   ```bash
   # Add to .gitignore
   .env
   .env.local
   ```

2. **Use environment variables in production**
   ```python
   # Don't do this:
   api_key = "sk-..."
   
   # Do this:
   from config.settings import settings
   api_key = settings.openrouter_api_key
   ```

3. **Rotate API keys regularly**
   - Update keys in provider dashboards
   - Update `.env` file
   - Restart services

4. **Limit API key permissions**
   - Use read-only keys where possible
   - Create service-specific keys
   - Set usage limits in provider settings

## 📊 Monitoring & Debugging

### Check Backend Health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/agents
```

### View Logs
```bash
# Terminal where backend is running shows detailed logs
# Look for:
# - ROUTING via Supervisor Agent
# - ROUTED TO: [agent_name]
# - Saved to memories
```

### Test Individual Agents
```bash
# In Python shell
import asyncio
from services.specialized_agents import research_agent

async def test():
    response = await research_agent.process(
        message="What is quantum computing?",
        user_id="test-user"
    )
    async for chunk in response:
        print(chunk, end="")

asyncio.run(test())
```

## 🆘 Troubleshooting

### "OPENROUTER_API_KEY not configured"
- Check `.env` file has `OPENROUTER_API_KEY=...`
- Verify key format is correct
- Restart backend

### "Anam session token failed"
- Check `ANAM_API_KEY` is valid
- Verify avatar/voice IDs are correct
- Check Anam API status

### "No memories stored"
- Verify `MEM0_ENABLED=true`
- Check `MEM0_API_KEY` is valid
- Look for errors in backend logs

### "Backend not reachable"
- Verify backend is running: `http://localhost:8000/health`
- Check firewall allows localhost:8000
- Restart backend: `uvicorn backend:app --port 8000 --reload`

### "Agent not routing correctly"
- Check supervisor logs for domain classification
- Verify user message is clear
- Look at routing decision output

## 🔄 Updating Configuration

To update settings:

1. **Edit `.env` file**
   ```bash
   ENABLE_VIDEO_AVATAR=false  # Turn off video mode
   ```

2. **Restart services**
   ```bash
   # Kill backend (Ctrl+C)
   # Restart: uvicorn backend:app --port 8000 --reload
   
   # Restart Streamlit (Ctrl+C)
   # Restart: streamlit run app_v2.py
   ```

3. **Changes take effect immediately**

## 📚 Additional Resources

- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [SerpApi Documentation](https://serpapi.com/docs)
- [Mem0 API Reference](https://docs.mem0.ai/)
- [Groq Console](https://console.groq.com/)

---

**Questions?** Check the README.md for architecture overview and usage examples.
