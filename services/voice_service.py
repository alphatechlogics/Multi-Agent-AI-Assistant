"""Voice service for STT and TTS operations using Groq API."""
import io
from typing import Optional
from config.settings import settings


class VoiceService:
    """Service for voice interactions (STT and TTS) using Groq API."""

    def __init__(self):
        """Initialize voice service with Groq client."""
        self.groq_client = None
        self.openai_client = None
        
        if settings.groq_api:
            from groq import AsyncGroq
            self.groq_client = AsyncGroq(api_key=settings.groq_api.strip())
        
        # OpenAI client for TTS (Groq doesn't have native TTS yet)
        if settings.openai_api_key:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio using Groq (Whisper).
        
        Args:
            audio_bytes: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        if not self.groq_client:
            print("GROQ_API not configured for STT")
            return ""

        try:
            # Create a file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"  # Groq requires a filename
            
            transcription = await self.groq_client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="text",
                temperature=0.0
            )
            
            result = str(transcription).strip()
            print(f"[STT] Transcribed: {result[:100]}...")
            return result
        except Exception as e:
            print(f"Error transcribing audio with Groq: {e}")
            return ""

    async def text_to_speech(self, text: str, voice: str = "alloy") -> Optional[bytes]:
        """
        Convert text to speech using OpenAI TTS API (high quality).
        Falls back to gTTS if OpenAI is not configured.
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            
        Returns:
            Audio bytes (mp3) or None
        """
        if not text or not text.strip():
            print("[TTS] No text provided")
            return None
            
        # Try OpenAI TTS first (higher quality)
        if self.openai_client:
            try:
                print(f"[TTS] Using OpenAI TTS for text: {text[:50]}...")
                response = await self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text,
                    response_format="mp3"
                )
                
                # Get the audio bytes
                audio_bytes = response.content
                print(f"[TTS] Generated {len(audio_bytes)} bytes of audio")
                return audio_bytes
                
            except Exception as e:
                print(f"Error with OpenAI TTS: {e}, falling back to gTTS")
        
        # Fallback to gTTS (free but lower quality)
        return await self._gtts_fallback(text)
    
    async def _gtts_fallback(self, text: str) -> Optional[bytes]:
        """
        Fallback TTS using gTTS (Google Text-to-Speech).

        Args:
            text: Text to convert

        Returns:
            Audio bytes or None
        """
        try:
            from gtts import gTTS

            print(f"[TTS] Using gTTS fallback for text: {text[:50]}...")

            # Try different configurations if the first fails
            configs = [
                {'lang': 'en', 'slow': False, 'tld': 'com'},
                {'lang': 'en', 'slow': False, 'tld': 'co.uk'},
                {'lang': 'en', 'slow': True, 'tld': 'com'},  # Slower but clearer
            ]

            last_error = None
            for config in configs:
                try:
                    # Create a file-like object
                    fp = io.BytesIO()

                    # Generate speech
                    tts = gTTS(text=text, **config)
                    tts.write_to_fp(fp)

                    # Get bytes
                    fp.seek(0)
                    audio_bytes = fp.getvalue()

                    if audio_bytes and len(audio_bytes) > 1000:  # Ensure we got real audio
                        print(f"[TTS] Generated {len(audio_bytes)} bytes via gTTS (tld: {config.get('tld', 'com')})")
                        return audio_bytes
                    else:
                        print(f"[TTS] gTTS returned empty or too small audio ({len(audio_bytes) if audio_bytes else 0} bytes)")
                        continue

                except Exception as config_error:
                    last_error = config_error
                    print(f"[TTS] gTTS config failed (tld: {config.get('tld', 'com')}): {config_error}")
                    continue

            # If all configs failed
            print(f"[TTS] All gTTS configurations failed. Last error: {last_error}")
            return None

        except Exception as e:
            print(f"[TTS] Error with gTTS fallback: {e}")
            return None


# Global instance
voice_service = VoiceService()
