"""Tool integrations: SerpApi, Mem0, ChromaDB for specialized agents."""
from typing import Dict, List, Any, Optional

from config.settings import settings


class SerpApiService:
    """Service for SerpApi tool integrations (Google search, flights, jobs, recipes)."""

    def __init__(self):
        """Initialize SerpApi service."""
        if not settings.serpapi_key:
            raise ValueError("SERPAPI_KEY not configured")
        self.api_key = settings.serpapi_key
        self.base_url = "https://serpapi.com"

    async def search_news(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search for news articles."""
        import httpx
        async with httpx.AsyncClient() as client:
            params = {
                "q": query,
                "tbm": "nws",
                "api_key": self.api_key,
                "num": num_results,
            }
            try:
                response = await client.get(f"{self.base_url}/search", params=params)
                data = response.json()
                return data.get("news_results", [])
            except Exception as e:
                print(f"Error searching news: {e}")
                return []

    async def search_flights(
        self, 
        departure: str, 
        arrival: str, 
        date: str,
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for flight information."""
        import httpx
        async with httpx.AsyncClient() as client:
            params = {
                "engine": "google_flights",
                "departure_id": departure,
                "arrival_id": arrival,
                "outbound_date": date,
                "api_key": self.api_key,
                "num": num_results,
            }
            try:
                response = await client.get(f"{self.base_url}/search", params=params)
                data = response.json()
                return data.get("flights", [])
            except Exception as e:
                print(f"Error searching flights: {e}")
                return []

    async def search_hotels(
        self,
        location: str,
        check_in: str,
        check_out: str,
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for hotels."""
        import httpx
        async with httpx.AsyncClient() as client:
            params = {
                "engine": "google_hotels",
                "q": location,
                "check_in_date": check_in,
                "check_out_date": check_out,
                "api_key": self.api_key,
                "num": num_results,
            }
            try:
                response = await client.get(f"{self.base_url}/search", params=params)
                data = response.json()
                return data.get("hotels", [])
            except Exception as e:
                print(f"Error searching hotels: {e}")
                return []

    async def search_jobs(self, query: str, location: str = "", num_results: int = 5) -> List[Dict[str, Any]]:
        """Search for jobs using SerpApi Google Jobs."""
        import httpx
        async with httpx.AsyncClient() as client:
            params = {
                "engine": "google_jobs",
                "q": query,
                "api_key": self.api_key,
                "num": num_results,
            }
            if location:
                params["location"] = location
                
            try:
                response = await client.get(f"{self.base_url}/search", params=params)
                data = response.json()
                return data.get("jobs_results", [])
            except Exception as e:
                print(f"Error searching jobs: {e}")
                return []

    async def search_recipes(
        self, 
        query: str, 
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for recipes with ratings and ingredients."""
        import httpx
        async with httpx.AsyncClient() as client:
            params = {
                "q": query,
                "tbm": "lcl",  # Local results which include recipes
                "api_key": self.api_key,
                "num": num_results,
            }
            try:
                response = await client.get(f"{self.base_url}/search", params=params)
                data = response.json()
                # Return local/recipe results
                return data.get("local_results", [])
            except Exception as e:
                print(f"Error searching recipes: {e}")
                return []


class Mem0Service:
    """Service for Mem0 integration - persistent long-term memory using official SDK."""

    def __init__(self):
        """Initialize Mem0 service with official SDK."""
        if not settings.mem0_api_key:
            raise ValueError("MEM0_API_KEY not configured")
        from mem0 import MemoryClient
        self.client = MemoryClient(api_key=settings.mem0_api_key)

    async def add_memory(
        self,
        user_id: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add a memory for a user."""
        try:
            result = self.client.add(
                messages=message,
                user_id=user_id,
                metadata=metadata or {}
            )
            return result if result else {}
        except Exception as e:
            print(f"Error adding memory: {e}")
            return {}

    async def retrieve_memories(
        self,
        user_id: str,
        query: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve memories for a user."""
        try:
            # For v2, filters are often required.
            # Passing filters as a dictionary is the standard way in many v2 SDKs.
            filters = {"user_id": user_id}
            
            if query:
                results = self.client.search(query, filters=filters, limit=limit)
            else:
                # Use get_all with filters if strictly supported, or search with wildcard/generic query + filters
                # If get_all doesn't accept filters in this SDK version, we fall back to search.
                # Let's try get_all with filters first as per error hint.
                try:
                    results = self.client.get_all(filters=filters, limit=limit)
                except Exception:
                    # Fallback to search with a generic query if get_all fails
                    results = self.client.search(query="*", filters=filters, limit=limit)
            
            return results if results else []
        except Exception as e:
            print(f"Error retrieving memories: {e}")
            return []

    async def delete_memory(
        self,
        memory_id: str
    ) -> bool:
        """Delete a specific memory."""
        try:
            self.client.delete(memory_id)
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False


class ChromaDBService:
    """Service for ChromaDB - multi-PDF RAG with Groq."""

    def __init__(self):
        """Initialize ChromaDB service."""
        try:
            import chromadb
            self.client = chromadb.PersistentClient(
                path=settings.chromadb_persist_directory
            )
            self.collection = self.client.get_or_create_collection(
                name=settings.chromadb_collection_name
            )
        except Exception as e:
            print(f"Error initializing ChromaDB: {e}")
            self.client = None
            self.collection = None

    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """Add documents to ChromaDB collection."""
        try:
            if not self.collection:
                return False
                
            if not ids:
                ids = [f"doc_{i}" for i in range(len(documents))]
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas or [{}] * len(documents),
                ids=ids,
            )
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False

    async def query_documents(
        self,
        query: str,
        num_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Query documents from ChromaDB."""
        try:
            if not self.collection:
                return []
                
            results = self.collection.query(
                query_texts=[query],
                n_results=num_results
            )
            
            formatted_results = []
            if results and results.get("documents"):
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "document": doc,
                        "distance": results.get("distances", [[]])[0][i] if results.get("distances") else None,
                        "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else None,
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Error querying documents: {e}")
            return []

    async def generate_rag_response(
        self,
        query: str,
        context_documents: Optional[List[str]] = None
    ) -> str:
        """Generate response using RAG with Groq LLM."""
        try:
            from groq import AsyncGroq
            
            if not context_documents:
                context_documents = await self.query_documents(query)
                context_documents = [doc.get("document", "") for doc in context_documents]
            
            context = "\n\n".join(context_documents)
            
            client = AsyncGroq(api_key=settings.groq_api_key)
            message = await client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful assistant. Use the following context to answer the user's question:\n\n{context}"
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            
            return message.choices[0].message.content
        except Exception as e:
            print(f"Error generating RAG response: {e}")
            return ""


# Global service instances
serpapi_service = SerpApiService()
mem0_service = Mem0Service()
chromadb_service = ChromaDBService()
