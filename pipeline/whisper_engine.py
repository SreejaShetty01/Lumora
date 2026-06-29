import streamlit as st

@st.cache_resource
def get_whisper_model():
    # Lazy import to avoid loading it on application startup
    from faster_whisper import WhisperModel
    return WhisperModel("base", device="cpu", compute_type="int8")

class WhisperEngine:
    def transcribe(self, audio_path):
        """Transcribe audio file to text."""
        model = get_whisper_model()
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        full_transcript = []
        for segment in segments:
            full_transcript.append(segment.text)
            
        return " ".join(full_transcript)
