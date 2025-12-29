# Development Guide

## Adding New Specialized Agents

This guide explains how to add new specialized agents to the system.

## 1. Create Agent Class

In `services/specialized_agents.py`, add a new agent:

```python
class MyDomainAgent(BaseSpecializedAgent):
    """Agent for my domain."""

    def __init__(self):
        super().__init__("my_domain")

    async def process(
        self,
        message: str,
        user_id: str,
        user_memories: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process queries for my domain."""
        yield "🔄 Processing your request...\n"
        
        # Get user context
        context = await self._get_user_context(user_id)
        
        # Use tools (SerpApi, ChromaDB, etc.)
        # Build response
        
        # Stream response chunks
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        yield response.content
        
        # Save to memory
        await mem0_service.add_memory(
            user_id=user_id,
            message=f"My Domain Query: {message[:100]}",
            metadata={"domain": "my_domain", "query": message}
        )
```

## 2. Register Agent

In `services/specialized_agents.py`, add to registry:

```python
my_domain_agent = MyDomainAgent()

AGENT_REGISTRY = {
    "research": research_agent,
    "finance": finance_agent,
    # ... existing agents ...
    "my_domain": my_domain_agent,  # Add here
}
```

## 3. Update Configuration

In `config/settings.py`, update agent domains:

```python
agent_domains: List[str] = [
    "research",
    "finance",
    "travel",
    "shopping",
    "jobs",
    "recipes",
    "my_domain",  # Add here
]
```

## 4. Update Supervisor Routing

In `services/supervisor_agent.py`, add routing method:

```python
async def _route_to_my_domain(self, state: AgentState) -> Dict[str, Any]:
    """Route to my domain agent."""
    return {
        "next_agent": "my_domain_agent",
        "conversation_context": {
            **state.get("conversation_context", {}),
            "agent": "my_domain"
        }
    }
```

And add to the routing graph:

```python
def _build_routing_graph(self):
    workflow = StateGraph(AgentState)
    
    # ... existing nodes ...
    workflow.add_node("my_domain_agent", self._route_to_my_domain)
    
    # ... existing edges ...
```

## 5. Add Domain-Specific Tools

Create new tool methods in `services/tools_service.py`:

```python
class MyDomainToolsService:
    """Tools for my domain."""
    
    async def search_my_data(self, query: str) -> List[Dict[str, Any]]:
        """Search domain-specific data."""
        # Implementation
        pass
```

Or extend existing services:

```python
class SerpApiService:
    # ... existing methods ...
    
    async def search_my_domain(self, query: str) -> List[Dict[str, Any]]:
        """Search for my domain data."""
        import httpx
        async with httpx.AsyncClient() as client:
            params = {
                "q": query,
                "engine": "google",  # or custom engine
                "api_key": self.api_key,
            }
            try:
                response = await client.get(f"{self.base_url}/search", params=params)
                return response.json().get("results", [])
            except Exception as e:
                print(f"Error: {e}")
                return []
```

## 6. Test Agent

```python
# test_my_agent.py
import asyncio
from services.specialized_agents import my_domain_agent

async def test():
    response_text = ""
    async for chunk in await my_domain_agent.process(
        message="Test query",
        user_id="test-user"
    ):
        response_text += chunk
        print(chunk, end="")
    
    print(f"\nFull response length: {len(response_text)}")

asyncio.run(test())
```

Run with:
```bash
python test_my_agent.py
```

## Adding Custom Tools

### Create Tool Class

```python
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    query: str = Field(description="Search query")
    limit: int = Field(default=5, description="Number of results")

class MyTool(BaseTool):
    name = "my_tool"
    description = "Description of what my tool does"
    args_schema = MyToolInput
    
    def _run(self, query: str, limit: int = 5):
        # Synchronous implementation
        pass
    
    async def _arun(self, query: str, limit: int = 5):
        # Async implementation
        pass
```

### Use in Agent

```python
async def process(self, message: str, user_id: str, ...):
    tool = MyTool()
    
    result = await tool._arun(
        query=message,
        limit=5
    )
    
    yield result
```

## Modifying Supervisor Routing Logic

The supervisor uses intent classification to route messages. To customize:

### Option 1: Update Classification Prompt

In `services/supervisor_agent.py`:

```python
async def _classify_domain(self, state: AgentState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    last_message = messages[-1].content if messages else ""

    # Customize this prompt for better routing
    classification_prompt = f"""
    Analyze the user query and classify it to one of these domains:
    {', '.join(self.domains)}
    
    Consider: intent, keywords, context
    
    User Query: {last_message}
    
    Respond with ONLY the domain name, nothing else.
    """
```

### Option 2: Add Keyword-Based Routing

```python
async def _classify_domain(self, state: AgentState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    last_message = (messages[-1].content if messages else "").lower()

    # Keyword-based routing
    keywords = {
        "research": ["research", "study", "article", "information"],
        "finance": ["stock", "money", "investment", "finance"],
        "my_domain": ["keyword1", "keyword2", "keyword3"],
    }
    
    for domain, kws in keywords.items():
        if any(kw in last_message for kw in kws):
            return {"next_agent": domain, ...}
    
    # Fallback to LLM classification
    # ...
```

## Memory Management

### Access User Memories

```python
# In any agent
memories = await mem0_service.retrieve_memories(
    user_id=user_id,
    query="relevant past interactions",
    limit=10
)

# Use in context
for memory in memories:
    # Build context from memories
    context += f"Past: {memory['message']}\n"
```

### Add Custom Metadata

```python
await mem0_service.add_memory(
    user_id=user_id,
    message="User action description",
    metadata={
        "domain": "my_domain",
        "action": "search",
        "query": message,
        "timestamp": time.time(),
        "custom_field": "custom_value"
    }
)
```

## Database/Vector Store Integration

### ChromaDB Example

```python
# Add documents
docs = ["Document 1", "Document 2", "Document 3"]
await chromadb_service.add_documents(
    documents=docs,
    metadatas=[
        {"source": "file1", "type": "pdf"},
        {"source": "file2", "type": "pdf"},
        {"source": "file3", "type": "txt"},
    ]
)

# Query documents
results = await chromadb_service.query_documents(
    query="search term",
    num_results=5
)

# Generate RAG response
response = await chromadb_service.generate_rag_response(
    query="user question",
    context_documents=[r["document"] for r in results]
)
```

## Streaming Response Best Practices

When creating async generators for streaming:

```python
async def process(self, message: str, user_id: str, ...) -> AsyncGenerator[str, None]:
    """Process message and yield chunks."""
    
    # Yield initial feedback
    yield "🔄 Processing...\n"
    
    # Get results
    results = await some_tool()
    
    # Stream formatted results
    for result in results:
        yield f"• {result['title']}\n"
    
    # Stream final synthesis
    response = await self.llm.ainvoke([...])
    yield response.content
    
    # Yield completion
    yield "\n✅ Done!"
```

## Error Handling

```python
async def process(self, message: str, user_id: str, ...) -> AsyncGenerator[str, None]:
    try:
        # Process
        yield response
    except Exception as e:
        # Log error
        print(f"[{self.domain}Agent] Error: {e}")
        
        # Yield user-friendly error
        yield f"I encountered an error: {str(e)}"
        
        # Optionally log to memory
        await mem0_service.add_memory(
            user_id=user_id,
            message=f"Error in {self.domain} agent: {str(e)}",
            metadata={"type": "error", "domain": self.domain}
        )
```

## Testing Multi-Agent System

### Integration Test

```python
# test_integration.py
import asyncio
from services.supervisor_agent import supervisor_agent
from services.specialized_agents import AGENT_REGISTRY

async def test_routing():
    test_queries = [
        ("Show me the latest AI news", "research"),
        ("What's the stock price of NVDA?", "finance"),
        ("Find me flights to Paris", "travel"),
        ("Recommend a product", "shopping"),
        ("I need a new job", "jobs"),
        ("Give me a recipe", "recipes"),
    ]
    
    for query, expected_agent in test_queries:
        routing = await supervisor_agent.route(
            message=query,
            user_id="test-user"
        )
        
        actual_agent = routing["recommended_agent"]
        status = "✓" if actual_agent == expected_agent else "✗"
        print(f"{status} '{query}' → {actual_agent} (expected: {expected_agent})")

asyncio.run(test_routing())
```

## Performance Optimization

### Caching Results

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_agent_config(domain: str):
    """Cache agent configurations."""
    return AGENT_REGISTRY[domain]
```

### Parallel Processing

```python
import asyncio

# Process multiple agents in parallel
tasks = [
    agent1.process(message, user_id),
    agent2.process(message, user_id),
]

results = await asyncio.gather(*tasks)
```

### Batch Operations

```python
# Add multiple memories at once
memories = [
    {"user_id": "user1", "message": "..."},
    {"user_id": "user2", "message": "..."},
]

tasks = [
    mem0_service.add_memory(**m)
    for m in memories
]

await asyncio.gather(*tasks)
```

## Debugging

### Enable Detailed Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In agent code
logger.debug(f"Processing: {message}")
logger.debug(f"Agent context: {context}")
logger.debug(f"Tool result: {result}")
```

### Inspect State

```python
# In supervisor agent
print(f"Current state: {json.dumps(state, indent=2, default=str)}")

# In specialized agent
print(f"User memories: {user_memories}")
print(f"Message history: {conversation_history}")
```

## Deployment Considerations

- **Scalability:** Use async/await throughout
- **Memory:** Monitor ChromaDB and Mem0 usage
- **Costs:** Track API calls to SerpApi, Cerebras, etc.
- **Latency:** Optimize LLM calls and tool lookups
- **Reliability:** Add retry logic and error handling

---

See README.md for architecture overview and CONFIG_GUIDE.md for configuration details.
