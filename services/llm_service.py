"""LLM service for Groq-powered LLM interactions."""
import json
from typing import AsyncGenerator, List, Dict, Any, Optional, cast
from config import settings


class LLMService:
    """Service for LLM interactions using Groq API."""

    def __init__(self):
        """Initialize LLM service with Groq."""
        if not settings.groq_api:
            raise ValueError("GROQ_API not configured")
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.groq_api
        )

    async def stream_chat_completion(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
    ) -> AsyncGenerator[str, None]:
        """Stream chat completion from Groq LLM."""
        # Prepend system message
        openai_messages = [{"role": "system", "content": system_prompt}]
        openai_messages.extend(messages)

        try:
            # Stream response
            stream = await self.client.chat.completions.create(
                model=settings.primary_llm_model,
                messages=cast(Any, openai_messages),
                stream=True,
                temperature=0.8,
                max_tokens=2048,
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            # If streaming fails, try non-streaming
            print(f"\nStreaming failed, using non-streaming mode: {e}")
            response = await self.client.chat.completions.create(
                model=settings.primary_llm_model,
                messages=cast(Any, openai_messages),
                stream=False,
                temperature=0.8,
                max_tokens=2048,
            )
            if response.choices and response.choices[0].message.content:
                yield response.choices[0].message.content

    async def summarize_text(self, text: str, max_words: int = 150) -> str:
        """
        Generate a concise, spoken-style summary using Groq.
        
        This summary is optimized for TTS playback - conversational and easy to listen to.
        
        Args:
            text: The text to summarize
            max_words: Target word count for the summary (default 150 for TTS)
            
        Returns:
            A summarized version of the text suitable for audio playback
        """
        if not text or not text.strip():
            print("[Summarize] No text provided")
            return ""
            
        if not settings.groq_api:
            print("[Summarize] GROQ_API not configured")
            return text[:300] + "..."
        
        # Clean the input text
        clean_text = text.strip()[:12000]  # Limit input size
        
        prompt = f"""Create a concise, conversational summary of the following text. 
The summary should be:
- About {max_words} words maximum
- Written in a natural, spoken style (as if explaining to a friend)
- Cover the key points and main takeaways
- Avoid bullet points or lists - use flowing sentences
- Easy to understand when read aloud

Text to summarize:
---
{clean_text}
---

Concise spoken summary:"""

        try:
            print(f"[Summarize] Processing text of {len(clean_text)} chars...")
            
            response = await self.client.chat.completions.create(
                model=settings.primary_llm_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates clear, concise summaries suitable for audio playback. Keep your summaries conversational and natural-sounding."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.5,  # Lower temp for more consistent summaries
                max_tokens=500,
                stream=False
            )
            
            content = response.choices[0].message.content
            if content and content.strip():
                summary = content.strip()
                print(f"[Summarize] Generated summary of {len(summary)} chars")
                return summary
            
            print("[Summarize] Empty response from LLM")
            return text[:300] + "..."
            
        except Exception as e:
            print(f"[Summarize] Error: {e}")
            import traceback
            traceback.print_exc()
            return text[:300] + "..."

# Global service instance
llm_service = LLMService()
