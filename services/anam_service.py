"""Anam AI service for avatar management and video interactions."""
import httpx
import json
from typing import Dict, Any, Optional
from config.settings import settings


class AnamService:
    """Service for interacting with Anam AI API for video avatar."""

    def __init__(self):
        """Initialize Anam AI service."""
        self.api_key = settings.anam_api_key
        self.base_url = settings.anam_api_base_url or "https://api.anam.ai"
        self.avatar_id = settings.anam_avatar_id
        self.voice_id = settings.anam_voice_id
        self.headers = {
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
            "Content-Type": "application/json",
        }
        self.enabled = bool(self.api_key)

    def is_configured(self) -> bool:
        """Check if Anam AI is properly configured."""
        return bool(self.api_key)

    async def create_session_token(
        self,
        persona_name: str = "AI Assistant",
        system_prompt: Optional[str] = None,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None,
        llm_id: Optional[str] = None,
        max_session_length_seconds: Optional[int] = 600,
    ) -> Optional[Dict[str, Any]]:
        """
        Create a session token for initializing an Anam persona.

        Args:
            persona_name: Name of the persona
            system_prompt: Custom system prompt for the persona
            avatar_id: Avatar ID
            voice_id: Voice ID
            llm_id: LLM ID
            max_session_length_seconds: Maximum session duration in seconds

        Returns:
            Dict containing sessionToken and other session info, or None on error
        """
        # Use defaults from settings if not provided
        avatar_id = avatar_id or self.avatar_id
        voice_id = voice_id or self.voice_id

        # Default system prompt
        if not system_prompt:
            system_prompt = (
                f"You are {persona_name}, a helpful AI assistant. "
                "Provide accurate, conversational responses. "
                "Keep your answers concise and engaging."
            )

        # If API is configured, try to create real session
        if self.enabled:
            try:
                url = f"{self.base_url}/v1/auth/session-token"

                if llm_id is None:
                    llm_id = "CUSTOMER_CLIENT_V1"

                payload = {
                    "personaConfig": {
                        "name": persona_name,
                        "avatarId": avatar_id,
                        "voiceId": voice_id,
                        "llmId": llm_id,
                        "systemPrompt": system_prompt,
                    }
                }

                if max_session_length_seconds:
                    payload["personaConfig"]["maxSessionLengthSeconds"] = max_session_length_seconds

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        url, headers=self.headers, json=payload, timeout=30.0
                    )
                    response.raise_for_status()
                    result = response.json()

                    # Add metadata for UI
                    result["isDemo"] = False
                    result["personaName"] = persona_name
                    result["avatarId"] = avatar_id
                    result["voiceId"] = voice_id

                    return result

            except httpx.HTTPStatusError as e:
                print(f"Anam API HTTP error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                print(f"Anam API error: {e}")

        # Fallback to demo session
        return self._create_demo_session(persona_name, avatar_id, voice_id)

    def _create_demo_session(
        self,
        persona_name: str,
        avatar_id: Optional[str] = None,
        voice_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a demo session when API is not available."""
        return {
            "isDemo": True,
            "sessionToken": f"demo-token-{persona_name.lower().replace(' ', '-')}",
            "sessionId": f"demo-session-{persona_name.lower().replace(' ', '-')}",
            "personaName": persona_name,
            "avatarId": avatar_id or "demo-avatar",
            "voiceId": voice_id or "demo-voice",
            "personaConfig": {
                "name": persona_name,
                "avatarId": avatar_id or "demo-avatar",
                "voiceId": voice_id or "demo-voice",
                "mode": "demo"
            }
        }

    async def send_message(
        self,
        session_token: str,
        message: str,
        session_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Send a message to the avatar to generate a response.

        Args:
            session_token: The session token from create_session_token
            message: The message to send
            session_id: Optional session ID

        Returns:
            Response data including video/audio URL, or None on error
        """
        if not self.enabled:
            # Demo mode - return mock response
            return {
                "isDemo": True,
                "message": message,
                "response": f"Demo response to: {message}",
                "videoUrl": None,
                "audioUrl": None
            }

        try:
            url = f"{self.base_url}/v1/sessions/{session_id or 'current'}/messages"

            headers = {
                **self.headers,
                "X-Session-Token": session_token
            }

            payload = {
                "message": message,
                "generateVideo": True,
                "generateAudio": True
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, headers=headers, json=payload, timeout=60.0
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            print(f"Error sending message to avatar: {e}")
            return None

    async def end_session(self, session_id: str) -> bool:
        """
        End an avatar session.

        Args:
            session_id: The session ID to end

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or session_id.startswith("demo-"):
            return True

        try:
            url = f"{self.base_url}/v1/sessions/{session_id}"

            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    url, headers=self.headers, timeout=30.0
                )
                response.raise_for_status()
                return True

        except Exception as e:
            print(f"Error ending session: {e}")
            return False

    def get_embed_html(
        self, 
        session_token: str, 
        width: int = 400, 
        height: int = 300,
        speaking_text: Optional[str] = None
    ) -> str:
        """
        Get HTML embed code for the avatar video player with Anam SDK.

        Args:
            session_token: The session token
            width: Player width
            height: Player height
            speaking_text: Optional text for the avatar to speak on load

        Returns:
            HTML string for embedding
        """
        if session_token.startswith("demo-"):
            # Demo mode - show animated placeholder with pulsing effect
            return f'''
            <div style="
                width: {width}px; 
                height: {height}px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: white;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            ">
                <div style="font-size: 64px; margin-bottom: 16px; animation: pulse 2s infinite;">🤖</div>
                <div style="font-size: 18px; font-weight: 600;">AI Avatar</div>
                <div style="font-size: 14px; opacity: 0.8; margin-top: 8px;">Demo Mode Active</div>
                <div style="font-size: 12px; opacity: 0.6; margin-top: 4px;">Configure ANAM_API_KEY for live video</div>
                <style>
                    @keyframes pulse {{
                        0%, 100% {{ transform: scale(1); }}
                        50% {{ transform: scale(1.1); }}
                    }}
                </style>
            </div>
            '''

        # Escape the speaking text for JavaScript
        escaped_text = ""
        if speaking_text:
            escaped_text = speaking_text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ").replace("\r", "")

        # Real Anam AI embed using the official JS SDK
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    background: #0a0a0f; 
                    display: flex; 
                    justify-content: center; 
                    align-items: center;
                    height: 100vh;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }}
                .avatar-container {{
                    width: {width}px;
                    height: {height}px;
                    border-radius: 12px;
                    overflow: hidden;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    position: relative;
                }}
                #persona-video {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    border-radius: 12px;
                }}
                .loading-overlay {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    transition: opacity 0.5s ease;
                }}
                .loading-overlay.hidden {{ opacity: 0; pointer-events: none; }}
                .spinner {{
                    width: 40px;
                    height: 40px;
                    border: 3px solid rgba(255,255,255,0.3);
                    border-top-color: white;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 16px;
                }}
                @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
                .status {{ font-size: 14px; opacity: 0.9; }}
                .error {{ color: #ff6b6b; font-size: 12px; margin-top: 8px; }}
            </style>
        </head>
        <body>
            <div class="avatar-container">
                <video id="persona-video" autoplay playsinline></video>
                <div id="loading-overlay" class="loading-overlay">
                    <div class="spinner"></div>
                    <div class="status" id="status-text">Connecting to avatar...</div>
                    <div class="error" id="error-text"></div>
                </div>
            </div>

            <script type="module">
                import {{ createClient }} from "https://esm.sh/@anam-ai/js-sdk@latest";
                
                const sessionToken = "{session_token}";
                const speakingText = "{escaped_text}";
                
                const statusText = document.getElementById('status-text');
                const errorText = document.getElementById('error-text');
                const loadingOverlay = document.getElementById('loading-overlay');
                
                async function initAvatar() {{
                    try {{
                        statusText.textContent = 'Initializing avatar...';
                        
                        // Create the Anam client with session token
                        const anamClient = createClient(sessionToken);
                        
                        statusText.textContent = 'Starting video stream...';
                        
                        // Stream to the video element
                        await anamClient.streamToVideoElement('persona-video');
                        
                        // Hide loading overlay when video starts
                        loadingOverlay.classList.add('hidden');
                        
                        // If we have text to speak, make the avatar say it
                        if (speakingText && speakingText.trim()) {{
                            // Small delay to ensure connection is stable
                            setTimeout(async () => {{
                                try {{
                                    await anamClient.talk(speakingText);
                                    console.log('Avatar speaking:', speakingText);
                                }} catch (talkError) {{
                                    console.error('Talk error:', talkError);
                                }}
                            }}, 1000);
                        }}
                        
                        console.log('Avatar connected successfully');
                        
                    }} catch (error) {{
                        console.error('Avatar initialization error:', error);
                        statusText.textContent = 'Connection failed';
                        errorText.textContent = error.message || 'Unable to connect';
                    }}
                }}
                
                // Initialize when the page loads
                initAvatar();
            </script>
        </body>
        </html>
        '''


# Global service instance
anam_service = AnamService()
