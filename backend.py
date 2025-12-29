import json
import time
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.llm_service import llm_service  # Cerebras only
from services.supervisor_agent import supervisor_agent
from services.specialized_agents import AGENT_REGISTRY
from services.tools_service import mem0_service
from config.settings import settings  


# -------------------------------
# Pydantic Models
# -------------------------------

class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


class SessionCreateRequest(BaseModel):
    user_id: str
    first_name: Optional[str] = "Demo"
    last_name: Optional[str] = None
    email: Optional[str] = None


class MultiModalRequest(BaseModel):
    """Request for multi-modal interaction."""
    user_id: str
    session_id: str
    message: str
    mode: str = "text"  # "text", "voice", "video"
    conversation_history: Optional[List[Message]] = None


# -------------------------------
# FastAPI App
# -------------------------------

app = FastAPI(
    title="Multi-Agent AI Assistant Backend",
    description="FastAPI backend with supervisor agent orchestration for specialized domains",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


# -------------------------------
# Health & Debug Endpoints
# -------------------------------

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "2.0.0", "mode": "multi-agent"}


@app.get("/agents")
async def list_agents():
    """List all available specialized agents."""
    return {
        "agents": list(AGENT_REGISTRY.keys()),
        "domains": settings.agent_domains,
        "interaction_modes": {
            "text_chat": settings.enable_text_chat,
            "video_avatar": settings.enable_video_avatar,
            "voice_agent": settings.enable_voice_agent,
        }
    }


# -------------------------------
# Session Management
# -------------------------------

@app.post("/session")
async def create_session(body: SessionCreateRequest):
    """
    Create a new session.
    Also initializes user in Mem0 for long-term memory.
    """
    try:
        session_id = f"session-{body.user_id}"

        # Initialize user in Mem0
        if settings.mem0_enabled:
            await mem0_service.add_memory(
                user_id=body.user_id,
                message=f"User {body.first_name} initialized.",
                metadata={
                    "session_id": session_id,
                    "created_at": str(time.time())
                }
            )

        return {
            "user_id": body.user_id,
            "session_id": session_id,
            "memory_enabled": settings.mem0_enabled,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Supervisor Agent Routing Endpoint
# -------------------------------

@app.post("/route")
async def route_message(payload: MultiModalRequest):
    """
    Route user message to appropriate specialized agent using supervisor.
    
    Returns routing decision with recommended agent.
    """
    try:
        # Get user's stored memories
        user_memories = None
        if settings.mem0_enabled:
            memories = await mem0_service.retrieve_memories(
                user_id=payload.user_id,
                limit=5
            )
            user_memories = {
                "memories": memories,
                "count": len(memories)
            }

        # Get routing decision from supervisor
        routing_decision = await supervisor_agent.route(
            message=payload.message,
            user_id=payload.user_id,
            conversation_history=[
                {"role": m.role, "content": m.content}
                for m in payload.conversation_history or []
            ],
            user_memories=user_memories,
        )

        return {
            "status": "routed",
            "recommended_agent": routing_decision["recommended_agent"],
            "classified_domain": routing_decision["classified_domain"],
            "context": routing_decision["context"],
            "session_id": payload.session_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------
# Multi-Agent Stream Endpoint
# -------------------------------

@app.post("/multi-agent/stream")
async def multi_agent_stream(payload: MultiModalRequest):
    """
    Main streaming endpoint for multi-agent interactions.
    
    Flow:
    1. Route message using supervisor agent
    2. Get specialized agent for domain
    3. Stream response from specialized agent
    4. Save to Mem0 for persistence
    """

    async def event_generator():
        """Generate streaming responses from appropriate agent."""
        try:
            print(f"\n{'='*60}")
            print(f"MULTI-AGENT REQUEST")
            print(f"User: {payload.user_id} | Session: {payload.session_id}")
            print(f"Message: {payload.message}")
            print(f"Mode: {payload.mode}")
            print(f"{'='*60}")

            # Step 1: Get user memories
            user_memories = None
            if settings.mem0_enabled:
                memories = await mem0_service.retrieve_memories(
                    user_id=payload.user_id,
                    limit=5
                )
                user_memories = {
                    "memories": memories,
                    "user_id": payload.user_id
                }

            # Step 2: Route via supervisor
            print(f"\nROUTING via Supervisor Agent...")
            routing_decision = await supervisor_agent.route(
                message=payload.message,
                user_id=payload.user_id,
                conversation_history=[
                    {"role": m.role, "content": m.content}
                    for m in payload.conversation_history or []
                ],
                user_memories=user_memories,
            )

            recommended_agent = routing_decision["recommended_agent"]
            print(f"ROUTED TO: {recommended_agent}")

            # Step 3: Get specialized agent
            agent = AGENT_REGISTRY.get(recommended_agent)
            if not agent:
                raise ValueError(f"Unknown agent: {recommended_agent}")

            # Step 4: Stream from specialized agent
            print(f"PROCESSING with {recommended_agent} agent...\n")
            
            full_response = ""
            async for chunk in agent.process(
                message=payload.message,
                user_id=payload.user_id,
                user_memories=user_memories,
            ):
                full_response += chunk
                payload_json = json.dumps({
                    "content": chunk,
                    "agent": recommended_agent,
                    "mode": payload.mode
                })
                yield f"data: {payload_json}\n\n"

            # Step 5: Save to memories
            print(f"\nSaving to memories...")
            
            # Save to Mem0
            if settings.mem0_enabled:
                await mem0_service.add_memory(
                    user_id=payload.user_id,
                    message=f"Used {recommended_agent} agent: {payload.message[:100]}",
                    metadata={
                        "agent": recommended_agent,
                        "mode": payload.mode,
                        "response_length": len(full_response),
                    }
                )

            print(f"Response saved. Length: {len(full_response)} chars")
            print(f"{'='*60}\n")

        except Exception as e:
            err_payload = json.dumps({"error": str(e), "content": f"Error: {str(e)}"})
            yield f"data: {err_payload}\n\n"
            print(f"ERROR: {e}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# -------------------------------
# Legacy: Single LLM Stream (for backward compatibility)
# -------------------------------

@app.post("/llm/stream")
async def llm_stream(
    payload: ChatRequest,
    session_id: str = Query(..., description="Session ID"),
):
    """
    Legacy single LLM streaming endpoint (backward compatible).
    For new implementations, use /multi-agent/stream instead.
    """

    messages: List[Message] = payload.messages

    if not messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    user_message: Optional[str] = None
    for m in reversed(messages):
        if m.role == "user":
            user_message = m.content
            break

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    async def event_generator():
        full_response: str = ""

        try:
            print(f"\n{'='*60}")
            print(f"LEGACY LLM STREAM for session: {session_id}")
            print(f"Message: {user_message}")
            print(f"{'='*60}")

            system_prompt = """
You are a helpful AI assistant. When provided with relevant information or context below, 
use it to answer the user's question accurately and completely. Always use the information 
provided to give thorough, detailed answers. Be conversational and friendly while being informative.
If the context contains the answer, state it clearly and add relevant details from the context.
""".strip()

            formatted_messages: List[Dict[str, Any]] = [
                {"role": m.role, "content": m.content} for m in messages
            ]

            print(f"STREAMING LLM RESPONSE...")

            chunk_count = 0
            async for chunk in llm_service.stream_chat_completion(
                messages=formatted_messages,
                system_prompt=system_prompt,
            ):
                if not chunk:
                    continue

                chunk_count += 1
                full_response += chunk
                payload = json.dumps({"content": chunk})
                yield f"data: {payload}\n\n"

            print(f"{'='*60}\n")

        except Exception as e:
            err_payload = json.dumps({"content": "Error: " + str(e)})
            yield f"data: {err_payload}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

