# Lumora - AI Lecture Intelligence Platform (MVP)

Lumora transforms lecture recordings into intelligent study material with a premium SaaS-style interface.

## Core Features

- **High-Accuracy Transcription**: Powered by `faster-whisper`.
- **Structured AI Notes**: Advanced summarization using Google's Gemini 2.5 Flash.
- **Contextual RAG Chat**: Ask questions about your lectures and get answers backed by vector search (`FAISS`).
- **Premium UI**: Minimalist, light-themed design inspired by world-class AI products.
- **Local Persistence**: Full lecture history and chat records stored in SQLite.

## Project Structure

- `app.py`: Multi-page routing and navigation hub.
- `pipeline/`: Core AI engines (Whisper, LLM, RAG).
- `views/`: Functional pages (Home, Upload, Dashboard, History, Settings).
- `database/`: Persistence layer and vector indexes.
- `assets/css/`: Modern SaaS design system.

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   streamlit run app.py
   ```

3. **Configure API**:
   Go to **Settings** and enter your **Gemini API Key** to enable AI features.

## Future Roadmap

- [ ] Speaker Diarization
- [ ] Adaptive Quizzes & Flashcards
- [ ] YouTube Lecture Import
- [ ] Knowledge Graph Visualization
