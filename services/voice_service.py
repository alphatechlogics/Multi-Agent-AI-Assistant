"""Voice service for STT and TTS operations."""
import io
from typing import Optional
from config.settings import settings

class VoiceService:
    """Service for voice interactions (STT and TTS)."""

    def __init__(self):
        """Initialize voice service."""
        pass

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribe audio using Groq (Whisper).
        
        Args:
            audio_bytes: Raw audio bytes
            
        Returns:
            Transcribed text
        """
        if not settings.groq_api:
            print("GROQ_API_KEY not found")
            return ""

        try:
            from groq import AsyncGroq
            
            # Ensure key is clean
            api_key = settings.groq_api.strip() if settings.groq_api else ""
            client = AsyncGroq(api_key=api_key)
            
            # Create a file-like object
            audio_file = io.BytesIO(audio_bytes)
            audio_file.name = "audio.wav"  # Groq requires a filename
            
            transcription = await client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3",
                response_format="text",
                temperature=0.0
            )
            
            return str(transcription)
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return ""

    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """
        Convert text to speech using gTTS (Google Text-to-Speech).
        
        Args:
            text: Text to convert
            
        Returns:
            Audio bytes or None
        """
        try:
            from gtts import gTTS
            
            # Create a file-like object
            fp = io.BytesIO()
            
            # Generate speech
            # lang='en', slow=False
            tts = gTTS(text=text, lang='en', slow=False)
            tts.write_to_fp(fp)
            
            # Get bytes
            fp.seek(0)
            return fp.getvalue()
            
        except Exception as e:
            print(f"Error generating speech with gTTS: {e}")
            return None

# Global instance
voice_service = VoiceService()
