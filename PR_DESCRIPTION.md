# 🚀 Unified Voice UI & Groq Standardization

## 📝 Summary
This PR significantly refines the user experience by unifying Text and Voice interactions into a single interface and standardizing the backend architecture to use **Groq** exclusively, removing the dependency on Cerebras.

## ✨ Key Changes

### 1. Unified User Interface
- **Merged Input Area**: Voice recorder and Text input are now stacked in a single "Chat" pane. Removed the separate "Voice Agent" sidebar tab.
- **Tabbed Responses**: Every assistant response now displays two tabs:
  - `📝 Summary`: A concise, spoken-style summary (auto-read by voice output).
  - `📄 Full Detail`: The complete markdown response with code and tables.
- **Auto-Scroll**: Improved flow for new messages.

### 2. Voice & Summarization Improvements
- **Enhanced Summarization**:
  - Summaries are now ~300 words (comprehensive yet spoken-style).
  - Switched from streaming generators to **stable, simple await calls** to prevent errors.
  - Uses **Groq (Mixtral 8x7b)** for fast summarization.
- **Stable TTS**: Reverted to `gTTS` (Google Text-to-Speech) to resolve audio length limitations present in other APIs.

### 3. Backend Standardization (Groq)
- **Single API Source**: All intelligence (Router, Agents, Summarizer) now uses the **Groq API**.
- **Removed Cerebras**: Deprecated `CEREBRAS_API_KEY` usage. System now relies solely on `GROQ_API`.
- **Model Update**: Default model set to `llama-3.1-8b-instant` / `mixtral-8x7b-32768` for high-speed inference.

## ⚙️ Configuration Changes
- Renamed `.env` variable: `GROQ_API_KEY` -> **`GROQ_API`**.
- Removed `.env` variable: `CEREBRAS_API_KEY`.

## 🧪 Testing
- Verified voice recording triggers auto-summary playback.
- Verified text input produces silent summary/detail tabs.
- Verified all agents (Research, Finance, etc.) route correctly via Groq.

---
*Ready for review and merge.*
