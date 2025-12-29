# Quick Start Guide

Get the multi-agent AI assistant running in 5 minutes!

## 📋 Prerequisites

- Python 3.12+
- UV package manager
- API keys (see below)

## ⚡ 5-Minute Setup

### 1. Clone and Install (1 min)

```bash
cd unifiedAgent
uv sync
```

### 2. Get API Keys (2 min)

Essential:
- **Cerebras**: https://console.cerebras.ai/ → `CEREBRAS_API_KEY`
- **OpenRouter** OR **Cerebras**: 
  - https://openrouter.ai/ → `OPENROUTER_API_KEY`, OR
  - https://console.cerebras.ai/ → `CEREBRAS_API_KEY`

Recommended (for full features):
- **SerpApi**: https://serpapi.com/ → `SERPAPI_KEY`
- **Mem0**: https://mem0.ai/ → `MEM0_API_KEY`
- **Groq**: https://console.groq.com/ → `GROQ_API_KEY`

Optional (for avatar):
- **Anam**: https://anam.ai/ → `ANAM_API_KEY`

### 3. Configure (1 min)

```bash
cp .env.example .env
# Edit .env and paste your API keys
```

Minimum `.env`:
```env
CEREBRAS_API_KEY=your_key
OPENROUTER_API_KEY=your_key
SERPAPI_KEY=your_key
```

### 4. Start Backend (1 min)

```bash
uvicorn backend:app --port 8000 --reload
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### 5. Start Frontend (Final min)

In another terminal:
```bash
streamlit run app_v2.py
```

Open browser to: http://localhost:8501

## 🎮 First Interaction

1. **Sidebar:** Enter your name → Click "Initialize New Session"
2. **Chat Tab:** Type a question:
   - "Find me a job in data science"
   - "Show me flights to Paris"
   - "Give me a chocolate cake recipe"
   - "What's happening in AI news?"
3. **Watch it route!** Response will show which agent handled your request

## 🤖 What You Get

The system automatically routes your requests to the right agent:

| Your Query | Agent | Tools |
|-----------|-------|-------|
| "Find flights to NYC" | ✈️ Travel | Flight search |
| "Job opportunities" | 💼 Jobs | Google Jobs |
| "Recipe ideas" | 👨🍳 Recipes | Recipe search |
| "Latest AI news" | 🔍 Research | News search + RAG |
| "Stock price NVDA" | 💰 Finance | Financial news |
| "Product recommendation" | 🛍️ Shopping | Product search |

## 📊 Features

### Text Chat
- 💬 Multi-turn conversations
- 🧠 Remembers context
- 🔄 Intelligent agent routing

### Agent Info Tab
- 🤖 See all 6 specialized agents
- 📚 Available tools for each
- 🎯 Current agent being used

### Memory Tab
- 🧠 Long-term memory (Mem0)
- 📝 All stored interactions
- 🔍 Search past conversations

## 🚀 Try These Queries

### Research Agent
- "What's the latest in quantum computing?"
- "Research machine learning frameworks"
- "Find recent AI breakthroughs"

### Travel Agent
- "I want to visit Tokyo next month"
- "Show me hotel options in London"
- "Find flights departing Friday"

### Jobs Agent
- "I'm looking for a senior developer role"
- "Find remote Python jobs"
- "Show me startup opportunities"

### Finance Agent
- "What's happening with tech stocks?"
- "Market analysis for AAPL"
- "Investment tips for beginners"

### Recipes Agent
- "I want to make pasta carbonara"
- "Show me vegan recipes"
- "Healthy dinner ideas"

### Shopping Agent
- "Find good laptops under $1000"
- "Best smartphone recommendations"
- "Comfortable office chairs"

## 🔧 Customization

### Disable Features

To skip video/voice setup, in `.env`:
```env
ENABLE_VIDEO_AVATAR=false
ENABLE_VOICE_AGENT=false
ENABLE_TEXT_CHAT=true
```

### Use Only Free APIs

Set `.env`:
```env
MEM0_ENABLED=false
GROQ_API_KEY=<get from console.groq.com>
# Groq has generous free tier
```

### Use Fallback LLM Only

If you only have OpenRouter:
```env
OPENROUTER_API_KEY=your_key
# Don't set CEREBRAS_API_KEY
# System will use Minimax M2
```

## 📚 Documentation

- **[CONFIG_GUIDE.md](CONFIG_GUIDE.md)** - All configuration options
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Add new agents
- **[README.md](README.md)** - Architecture overview

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check port is free
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Try different port
uvicorn backend:app --port 8001 --reload
```

### "API key not configured"
```bash
# Verify .env file
cat .env

# Check you copied keys correctly
# No spaces: OPENROUTER_API_KEY=sk-or-...
# Not: OPENROUTER_API_KEY = sk-or-...
```

### Agent not routing
```bash
# Check backend logs for:
# "ROUTED TO: [agent_name]"

# If missing, routing failed - check logs for errors
```

### Streamlit won't load
```bash
# Kill any old instances
pkill -f streamlit

# Restart
streamlit run app_v2.py
```

## 🆘 Getting Help

1. **Check logs** - Backend shows all decisions
2. **Test endpoint** - `curl http://localhost:8000/health`
3. **Review docs** - See docs above
4. **Check .env** - Verify all keys are set

## ✨ Next Steps

### For Users
- Explore different agents
- Try various queries
- Check memory growth
- Enable video/voice modes

### For Developers
- Add new agents (see [DEVELOPMENT.md](DEVELOPMENT.md))
- Create custom tools
- Optimize prompts
- Deploy to production

## 💡 Tips

1. **More natural queries** → Better routing
   - ✅ "I need a data science job"
   - ❌ "data science job"

2. **Different domains** → See routing in action
   - Try job, travel, recipe queries in one session

3. **Check Agent Info tab** → Learn what each does
   - See available tools
   - Understand capabilities

4. **Memory builds up** → Check Memory tab
   - See stored interactions
   - Build understanding of preferences

---

**Enjoy your multi-agent AI assistant! 🚀**
