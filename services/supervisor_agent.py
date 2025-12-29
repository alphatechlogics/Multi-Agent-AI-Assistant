"""Supervisor Agent using LangGraph for intelligent routing to specialized agents."""
from typing import Annotated, Any, Dict, List, Optional, TypedDict
from enum import Enum
import asyncio
import json

from langchain_core.messages import AnyMessage, BaseMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, StateGraph
# from langgraph.prebuilt.tool_executor import ToolExecutor
from pydantic import BaseModel, Field

from config.settings import settings


class AgentDomain(str, Enum):
    """Supported agent domains."""
    RESEARCH = "research"
    FINANCE = "finance"
    TRAVEL = "travel"
    SHOPPING = "shopping"
    JOBS = "jobs"
    RECIPES = "recipes"


class AgentState(TypedDict):
    """State for the supervisor agent graph."""
    messages: Annotated[List[AnyMessage], lambda x, y: x + y]
    next_agent: Optional[str]
    last_message: str
    conversation_context: Dict[str, Any]
    user_id: str
    user_memories: Optional[Dict[str, Any]]


class SupervisorAgent:
    """
    Supervisor agent that routes requests to specialized domain agents.
    
    Uses LangGraph for orchestration and provides intelligent routing based on:
    - Query context analysis
    - User intent detection
    - Domain classification
    - Tool availability
    """

    def __init__(self):
        """Initialize supervisor agent with routing logic."""
        self.domains = [domain.value for domain in AgentDomain]
        self.llm = self._init_llm()
        self.graph = self._build_routing_graph()

    def _init_llm(self):
        """Initialize the primary LLM for routing decisions."""
        from langchain_openai import ChatOpenAI
        
        return ChatOpenAI(
            model=settings.primary_llm_model,
            api_key=settings.cerebras_api_key,
            base_url="https://api.cerebras.ai/v1",
            temperature=0.3,  # Lower temp for routing decisions
        )

    def _build_routing_graph(self):
        """Build LangGraph for agent routing."""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("classifier", self._classify_domain)
        workflow.add_node("research_agent", self._route_to_research)
        workflow.add_node("finance_agent", self._route_to_finance)
        workflow.add_node("travel_agent", self._route_to_travel)
        workflow.add_node("shopping_agent", self._route_to_shopping)
        workflow.add_node("jobs_agent", self._route_to_jobs)
        workflow.add_node("recipes_agent", self._route_to_recipes)

        # Define routing logic
        def get_next_node(state: AgentState) -> str:
            domain = state.get("next_agent", "research")
            return f"{domain}_agent"

        # Add conditional edges
        workflow.add_conditional_edges(
            "classifier",
            get_next_node,
            {
                "research_agent": "research_agent",
                "finance_agent": "finance_agent",
                "travel_agent": "travel_agent",
                "shopping_agent": "shopping_agent",
                "jobs_agent": "jobs_agent",
                "recipes_agent": "recipes_agent",
            }
        )
        
        # Set entry point
        workflow.set_entry_point("classifier")

        return workflow.compile()

    async def _classify_domain(self, state: AgentState) -> Dict[str, Any]:
        """
        Classify user query to determine which specialized agent should handle it.
        """
        messages = state.get("messages", [])
        last_message = messages[-1].content if messages else ""

        classification_prompt = f"""
        You are the Supervisor Agent responsible for routing user queries to the most appropriate specialized agent.
        
        Analyze the user query and classify it into PREDISELY one of these domains:
        {', '.join(self.domains)}

        DOMAIN DEFINITIONS:
        - research: General knowledge, company history, "who is", "what is", news summaries, academic topics, technology explanations. Use this for questions about companies that are NOT specifically about stock metrics.
        - finance: Stock prices, ticker symbols, market cap, investment advice, portfolio management, currency exchange, financial reports.
        - travel: Trip planning, flights, hotels, tourist attractions, destination guides.
        - shopping: Product recommendations, reviews, buying advice, e-commerce, gifts.
        - jobs: Career advice, resume writing, job search, interview prep.
        - recipes: Cooking instructions, food ingredients, meal planning, dietary advice.

        GUIDELINES:
        - "Top stocks" or "stock price" -> finance
        - "Top tech companies" (general) -> research
        - "History of Apple" -> research
        - "Apple stock analysis" -> finance
        - If the query is ambiguous or falls between categories, prioritize 'research'.

        User Query: {last_message}

        Respond with ONLY the domain name (one word, lowercase). Do not add punctuation or explanation.
        """

        response = await self.llm.ainvoke([HumanMessage(content=classification_prompt)])
        domain = response.content.strip().lower()

        # Validate domain
        if domain not in self.domains:
            domain = "research"  # Default fallback

        return {
            "next_agent": domain,
            "conversation_context": {
                **state.get("conversation_context", {}),
                "classified_domain": domain,
            }
        }

    async def _route_to_research(self, state: AgentState) -> Dict[str, Any]:
        """Route to research agent."""
        return {
            "next_agent": "research_agent",
            "conversation_context": {
                **state.get("conversation_context", {}),
                "agent": "research"
            }
        }

    async def _route_to_finance(self, state: AgentState) -> Dict[str, Any]:
        """Route to finance agent."""
        return {
            "next_agent": "finance_agent",
            "conversation_context": {
                **state.get("conversation_context", {}),
                "agent": "finance"
            }
        }

    async def _route_to_travel(self, state: AgentState) -> Dict[str, Any]:
        """Route to travel agent."""
        return {
            "next_agent": "travel_agent",
            "conversation_context": {
                **state.get("conversation_context", {}),
                "agent": "travel"
            }
        }

    async def _route_to_shopping(self, state: AgentState) -> Dict[str, Any]:
        """Route to shopping agent."""
        return {
            "next_agent": "shopping_agent",
            "conversation_context": {
                **state.get("conversation_context", {}),
                "agent": "shopping"
            }
        }

    async def _route_to_jobs(self, state: AgentState) -> Dict[str, Any]:
        """Route to jobs agent."""
        return {
            "next_agent": "jobs_agent",
            "conversation_context": {
                **state.get("conversation_context", {}),
                "agent": "jobs"
            }
        }

    async def _route_to_recipes(self, state: AgentState) -> Dict[str, Any]:
        """Route to recipes agent."""
        return {
            "next_agent": "recipes_agent",
            "conversation_context": {
                **state.get("conversation_context", {}),
                "agent": "recipes"
            }
        }

    async def route(
        self,
        message: str,
        user_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_memories: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Route a message to the appropriate specialized agent.

        Args:
            message: User's input message
            user_id: User identifier for memory lookup
            conversation_history: Previous conversation messages
            user_memories: User's long-term memories from Mem0

        Returns:
            Routing decision with recommended agent and context
        """
        # Build initial state
        messages = [HumanMessage(content=message)]
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    from langchain_core.messages import AIMessage
                    messages.append(AIMessage(content=msg["content"]))

        state: AgentState = {
            "messages": messages,
            "next_agent": None,
            "last_message": message,
            "conversation_context": {},
            "user_id": user_id,
            "user_memories": user_memories,
        }

        # Invoke routing graph
        output = await self.graph.ainvoke(state)

        return {
            "recommended_agent": output.get("conversation_context", {}).get("agent", "research"),
            "classified_domain": output.get("conversation_context", {}).get("classified_domain"),
            "context": output.get("conversation_context", {}),
            "user_id": user_id,
        }


# Global supervisor instance
supervisor_agent = SupervisorAgent()
