"""Specialized domain agents: Research, Finance, Travel, Shopping, Jobs, Recipes."""
from typing import AsyncGenerator, List, Dict, Any, Optional
from abc import ABC, abstractmethod
import json

from langchain_core.messages import HumanMessage
from config.settings import settings
from services.tools_service import serpapi_service, mem0_service, chromadb_service


class BaseSpecializedAgent(ABC):
    """Base class for all specialized agents."""

    def __init__(self, domain: str):
        """Initialize specialized agent."""
        self.domain = domain
        self.llm = self._init_llm()
        
    def _init_llm(self):
        """Initialize LLM for the agent using Groq API."""
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=settings.primary_llm_model,
            api_key=settings.groq_api,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.7,
        )

    @abstractmethod
    async def process(
        self,
        message: str,
        user_id: str,
        user_memories: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process message and yield response."""
        pass

    async def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context including memories."""
        memories = await mem0_service.retrieve_memories(user_id)
        return {
            "user_id": user_id,
            "memories": memories,
        }


class ResearchAgent(BaseSpecializedAgent):
    """Research agent for web research, articles, and information gathering."""

    def __init__(self):
        super().__init__("research")

    async def process(
        self,
        message: str,
        user_id: str,
        user_memories: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process research queries."""
        yield "🔍 Searching for research information...\n"
        
        # Get user context and memories
        context = await self._get_user_context(user_id)
        
        # Search news for current information
        news_results = await serpapi_service.search_news(message, num_results=3)
        
        # Query ChromaDB for document context
        doc_results = await chromadb_service.query_documents(message)
        
        # Build prompt with context
        context_str = "Recent News Results:\n"
        for result in news_results:
            context_str += f"- {result.get('title', 'N/A')}: {result.get('snippet', '')}\n"
        
        context_str += "\nRelevant Documents:\n"
        for doc in doc_results[:3]:
            context_str += f"- {doc.get('document', '')[:200]}...\n"
        
        prompt = f"""
        You are an **Academic Research Scientist**. 
        Your goal is to provide deep, technical, and scientifically accurate information.
        
        Detailed Instructions:
        1. **Focus on Facts**: Prioritize peer-reviewed papers, official reports, and technical documentation.
        2. **Future Trends**: When asked about future years (e.g., 2025), interpret this as checking for pre-prints (arXiv), upcoming conference schedules (NeurIPS, CVPR), or roadmap announcements.
        3. **No Fluff**: Avoid generic advice. Give specific titles, dates, or theories where possible.
        4. **Scope**: Do NOT provide commercial product reviews, travel tips, or job listings unless explicitly crucial to the research context.

        User Query: {message}
        
        Context Information:
        {context_str}
        
        User Background: {json.dumps(user_memories or {})}
        
        Provide a structured, academic-grade response capable of citing sources.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        yield response.content
        
        # Save to memory if useful
        await mem0_service.add_memory(
            user_id=user_id,
            message=f"Researched: {message[:100]}",
            metadata={"domain": "research", "query": message}
        )


class FinanceAgent(BaseSpecializedAgent):
    """Finance agent for financial information, stock data, and investment advice."""

    def __init__(self):
        super().__init__("finance")

    async def process(
        self,
        message: str,
        user_id: str,
        user_memories: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process finance queries."""
        yield "💰 Analyzing financial information...\n"
        
        context = await self._get_user_context(user_id)
        
        # Search for financial news
        financial_info = await serpapi_service.search_news(
            f"{message} financial news",
            num_results=5
        )
        
        prompt = f"""
        You are a financial advisor. Provide financial insights based on the query.
        
        User Query: {message}
        
        Financial Context:
        {json.dumps(financial_info)}
        
        User Profile: {json.dumps(user_memories or {})}
        
        Provide balanced, informative financial guidance. Include disclaimers as appropriate.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        yield response.content
        
        await mem0_service.add_memory(
            user_id=user_id,
            message=f"Financial Query: {message[:100]}",
            metadata={"domain": "finance", "query": message}
        )


class TravelAgent(BaseSpecializedAgent):
    """Travel agent for flights, hotels, and trip planning."""

    def __init__(self):
        super().__init__("travel")

    async def process(
        self,
        message: str,
        user_id: str,
        user_memories: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process travel queries."""
        yield "✈️ Searching for travel options...\n"
        
        context = await self._get_user_context(user_id)
        
        # For now, provide general travel guidance
        # In real implementation, would parse message for departure, arrival, dates
        
        prompt = f"""
        You are a travel expert. Help plan the user's trip.
        
        User Query: {message}
        
        User Travel Preferences: {json.dumps(user_memories or {})}
        
        Provide detailed travel suggestions including flight/hotel tips,
        best times to visit, budget estimates, and local recommendations.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        yield response.content
        
        await mem0_service.add_memory(
            user_id=user_id,
            message=f"Travel Interest: {message[:100]}",
            metadata={"domain": "travel", "query": message}
        )


class ShoppingAgent(BaseSpecializedAgent):
    """Shopping agent for product recommendations and shopping assistance."""

    def __init__(self):
        super().__init__("shopping")

    async def process(
        self,
        message: str,
        user_id: str,
        user_memories: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process shopping queries."""
        yield "🛍️ Finding product recommendations...\n"
        
        context = await self._get_user_context(user_id)
        
        # Search for products
        search_results = await serpapi_service.search_news(
            f"{message} products reviews",
            num_results=5
        )
        
        prompt = f"""
        You are a shopping assistant. Recommend products based on the user's needs.
        
        User Query: {message}
        
        Available Products/Options:
        {json.dumps(search_results)}
        
        User Preferences: {json.dumps(user_memories or {})}
        
        Provide thoughtful recommendations with pros/cons and budget considerations.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        yield response.content
        
        await mem0_service.add_memory(
            user_id=user_id,
            message=f"Shopping Interest: {message[:100]}",
            metadata={"domain": "shopping", "query": message}
        )


class JobsAgent(BaseSpecializedAgent):
    """Jobs agent for job search and career advice."""

    def __init__(self):
        super().__init__("jobs")

    async def process(
        self,
        message: str,
        user_id: str,
        user_memories: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process job search queries."""
        yield "💼 Searching for job opportunities...\n"
        
        context = await self._get_user_context(user_id)
        
        # Parse job search query (simplified)
        # In real implementation, would extract job title, location, etc.
        
        jobs = await serpapi_service.search_jobs(message, num_results=5)
        
        prompt = f"""
        You are a **Career & Talent Acquisition Specialist**.
        Your goal is to help users find jobs, improve resumes, and navigate their careers.
        
        Detailed Instructions:
        1. **Scope Enforcer**: If the user's query is NOT about jobs, careers, hiring, or professional development, do not attempt to answer it. State clearly that you are the Jobs Agent and this query seems better suited for another specialist (like Research or Finance).
        2. **Job Search**: When asked for jobs, look for specific roles, locations, and requirements.
        3. **Career Advice**: Provide actionable tips for interviews, networking, and salary negotiation.
        4. **Anti-Hallucination**: Do not invent job postings. Use the provided search results.

        User Query: {message}
        
        Available Jobs:
        {json.dumps(jobs)}
        
        User Profile: {json.dumps(user_memories or {})}
        
        Provide professional career guidance or job listings.
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        yield response.content
        
        await mem0_service.add_memory(
            user_id=user_id,
            message=f"Job Search: {message[:100]}",
            metadata={"domain": "jobs", "query": message}
        )


class RecipesAgent(BaseSpecializedAgent):
    """Recipes agent for recipe discovery and cooking guidance."""

    def __init__(self):
        super().__init__("recipes")

    async def process(
        self,
        message: str,
        user_id: str,
        user_memories: Optional[Dict[str, Any]] = None,
    ) -> AsyncGenerator[str, None]:
        """Process recipe queries."""
        yield "👨🍳 Finding recipes for you...\n"
        
        context = await self._get_user_context(user_id)
        
        # Search for recipes
        recipes = await serpapi_service.search_recipes(message, num_results=5)
        
        prompt = f"""
        You are a culinary expert and recipe guide.
        
        User Query: {message}
        
        Recipe Options:
        {json.dumps(recipes)}
        
        User Dietary Preferences: {json.dumps(user_memories or {})}
        
        Provide detailed recipe recommendations with:
        - Ingredients and quantities
        - Step-by-step instructions
        - Cooking time and difficulty level
        - Nutritional information if available
        - Dietary notes and substitutions
        """
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        yield response.content
        
        await mem0_service.add_memory(
            user_id=user_id,
            message=f"Recipe Interest: {message[:100]}",
            metadata={"domain": "recipes", "query": message}
        )


# Global agent instances
research_agent = ResearchAgent()
finance_agent = FinanceAgent()
travel_agent = TravelAgent()
shopping_agent = ShoppingAgent()
jobs_agent = JobsAgent()
recipes_agent = RecipesAgent()

# Agent registry for routing
AGENT_REGISTRY = {
    "research": research_agent,
    "finance": finance_agent,
    "travel": travel_agent,
    "shopping": shopping_agent,
    "jobs": jobs_agent,
    "recipes": recipes_agent,
}
