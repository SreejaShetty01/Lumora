import streamlit as st
import os
import time
import tempfile
from database.manager import DatabaseManager
from pipeline.whisper_engine import WhisperEngine
from pipeline.llm_engine import LLMEngine
from pipeline.rag_engine import RAGEngine

def show():
    st.markdown("## 📤 Upload Lecture")
    st.markdown("<p class='secondary-text'>Upload audio or video recordings to generate intelligent study material.</p>", unsafe_allow_html=True)

    if not st.session_state.gemini_api_key:
        st.warning("⚠️ Please set your Gemini API Key in Settings before uploading.")
        return

    uploaded_file = st.file_uploader("Choose a file", type=["mp3", "wav", "m4a", "mp4"])

    if uploaded_file is not None:
        st.markdown(f"""
        <div class="saas-card">
            <strong>File:</strong> {uploaded_file.name}<br>
            <strong>Size:</strong> {uploaded_file.size / 1024 / 1024:.2f} MB
        </div>
        """, unsafe_allow_html=True)

        if st.button("Start Upload", use_container_width=True):
            if uploaded_file is None:
                st.error("Please select a file first.")
            else:
                process_file(uploaded_file)

def process_file(uploaded_file):
    db = DatabaseManager()
    whisper = WhisperEngine()
    llm = LLMEngine(st.session_state.gemini_api_key)
    rag = RAGEngine()

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        with st.spinner("Processing lecture... Please wait."):
            # Save file temporarily using Python's tempfile module
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(uploaded_file.getbuffer())
                file_path = temp_file.name
            
            # Store the uploaded file path in st.session_state
            st.session_state.uploaded_file_path = file_path

            # 1. Transcribe
            status_text.text("🎙️ Step 1/3: Transcribing Audio (faster-whisper)...")
            progress_bar.progress(10)
            transcript = whisper.transcribe(file_path)
            progress_bar.progress(40)

            # 2. Generate Notes
            status_text.text("🧠 Step 2/3: Generating Structured Notes (Gemini)...")
            notes = llm.generate_notes(transcript)
            progress_bar.progress(70)

            # 3. Create RAG Index
            status_text.text("🔍 Step 3/3: Indexing for Search (FAISS)...")
            faiss_path = f"database/indexes/{int(time.time())}"
            rag.create_vector_store(transcript, faiss_path)
            progress_bar.progress(90)

            # Save to DB
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lectures (title, file_path, status, transcript, notes, faiss_path)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (uploaded_file.name, file_path, 'done', transcript, notes, faiss_path))
            lecture_id = cursor.lastrowid
            conn.commit()
            conn.close()

            progress_bar.progress(100)
            status_text.success("✅ Processing Complete!")
            st.balloons()
            time.sleep(1) # Brief pause for user feedback
            
            # Store current lecture ID and navigate to Dashboard
            st.session_state.current_lecture_id = lecture_id
            st.session_state.navigation = "Dashboard"
            st.rerun()

    except Exception as e:
        st.error(f"Error processing lecture: {str(e)}")
        status_text.error("Processing failed.")
