import streamlit as st
import os
import time
import tempfile
import threading

def is_valid_youtube_url(url):
    import re
    pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+$'
    return bool(re.match(pattern, url))

def download_youtube_audio(url):
    import yt_dlp
    import tempfile
    import os
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(tempfile.gettempdir(), 'yt_download_%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info.get('title', 'YouTube Lecture')

def run_background_pipeline(lecture_id, transcript, faiss_path, gemini_api_key):
    """Executes long-running AI steps (Quiz, Flashcards, FAISS indexing) in the background."""
    from database.manager import DatabaseManager
    from pipeline.llm_engine import LLMEngine
    from pipeline.rag_engine import RAGEngine
    
    db = DatabaseManager()
    llm = LLMEngine(gemini_api_key)
    rag = RAGEngine()
    
    try:
        # 1. Generate Quiz (structured JSON)
        quiz = llm.generate_quiz(transcript)
        conn = db.get_connection()
        conn.execute("UPDATE lectures SET quiz=? WHERE id=?", (quiz, lecture_id))
        conn.commit()
        conn.close()
        
        # 2. Generate Flashcards (structured JSON)
        flashcards = llm.generate_flashcards(transcript)
        conn = db.get_connection()
        conn.execute("UPDATE lectures SET flashcards=? WHERE id=?", (flashcards, lecture_id))
        conn.commit()
        conn.close()
        
        # 3. Build FAISS Index
        rag.create_vector_store(transcript, faiss_path)
        
        # 4. Update status to done
        conn = db.get_connection()
        conn.execute("UPDATE lectures SET status='done' WHERE id=?", (lecture_id,))
        conn.commit()
        conn.close()
    except Exception as e:
        conn = db.get_connection()
        conn.execute("UPDATE lectures SET status='failed' WHERE id=?", (lecture_id,))
        conn.commit()
        conn.close()

def show():
    # Hero Section
    st.markdown("""
    <div style='text-align: center; padding: 40px 0 20px 0;'>
        <h1 style='font-size: 3.2rem; color: #0F172A; font-weight: 800; line-height: 1.2; letter-spacing: -0.03em;'>
            Turn Any Lecture Into Your Personal AI Tutor
        </h1>
        <p class='secondary-text' style='font-size: 1.2rem; max-width: 650px; margin: 15px auto 0 auto; color: #64748B;'>
            Transcribe, summarize, chat with, and study any lecture using AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Main Ingestion Form
    st.markdown('<div class="saas-card" style="max-width: 650px; margin: 0 auto; padding: 2rem; border-radius: 12px; background: white; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);">', unsafe_allow_html=True)

    # Primary Input
    youtube_url = st.text_input(
        "Paste YouTube Lecture URL", 
        placeholder="https://www.youtube.com/watch?v=...", 
        help="Paste a link to any public YouTube lecture recording"
    )

    # Separator
    st.markdown("""
    <div style="display: flex; align-items: center; text-align: center; margin: 20px 0; color: #94A3B8;">
        <div style="flex-grow: 1; height: 1px; background-color: #F1F5F9;"></div>
        <span style="padding: 0 10px; font-size: 0.8rem; font-weight: 600; color: #94A3B8;">OR</span>
        <div style="flex-grow: 1; height: 1px; background-color: #F1F5F9;"></div>
    </div>
    """, unsafe_allow_html=True)

    # Secondary Input
    uploaded_file = st.file_uploader(
        "Upload Audio or Video File", 
        type=["mp3", "wav", "m4a", "mp4"], 
        help="Supported formats: MP3, WAV, M4A, MP4"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Large Analyze Lecture Button
    analyze_clicked = st.button("Analyze Lecture", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Workflow Section
    st.markdown("""
    <div style="margin-top: 50px; text-align: center;">
        <p style="font-size: 0.9rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 20px;">How it works</p>
        <div style="display: flex; justify-content: center; align-items: center; max-width: 700px; margin: 0 auto; gap: 20px; flex-wrap: wrap;">
            <div class="saas-card" style="flex: 1; min-width: 180px; padding: 15px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;">
                <div style="font-size: 1.5rem; margin-bottom: 5px;">①</div>
                <div style="font-weight: 600; font-size: 0.9rem; color: #0F172A;">Lecture Input</div>
                <div style="font-size: 0.75rem; color: #64748B; margin-top: 5px;">Paste YouTube link or upload file</div>
            </div>
            <div style="color: #94A3B8; font-weight: bold; font-size: 1.2rem;">↓</div>
            <div class="saas-card" style="flex: 1; min-width: 180px; padding: 15px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;">
                <div style="font-size: 1.5rem; margin-bottom: 5px;">②</div>
                <div style="font-weight: 600; font-size: 0.9rem; color: #0F172A;">AI Processing</div>
                <div style="font-size: 0.75rem; color: #64748B; margin-top: 5px;">Whisper transcription & Gemini indexing</div>
            </div>
            <div style="color: #94A3B8; font-weight: bold; font-size: 1.2rem;">↓</div>
            <div class="saas-card" style="flex: 1; min-width: 180px; padding: 15px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px;">
                <div style="font-size: 1.5rem; margin-bottom: 5px;">③</div>
                <div style="font-weight: 600; font-size: 0.9rem; color: #0F172A;">Study Space</div>
                <div style="font-size: 0.75rem; color: #64748B; margin-top: 5px;">Notes, Chat, Quizzes, & Flashcards</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Process logic when button clicked
    if analyze_clicked:
        if not st.session_state.gemini_api_key:
            st.error("⚠️ AI Engine is disconnected. Please configure your Gemini API Key in the Settings page to analyze lectures.")
        elif youtube_url and not uploaded_file:
            process_lecture('youtube', youtube_url)
        elif uploaded_file:
            process_lecture('file', uploaded_file)
        elif youtube_url and uploaded_file:
            st.warning("Please provide either a YouTube URL or an uploaded file, not both.")
        else:
            st.error("Please provide a lecture to analyze (paste a YouTube URL or upload a file).")

def process_lecture(source_type, source_val):
    from database.manager import DatabaseManager
    from pipeline.whisper_engine import WhisperEngine
    from pipeline.llm_engine import LLMEngine

    db = DatabaseManager()
    whisper = WhisperEngine()
    llm = LLMEngine(st.session_state.gemini_api_key)

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        with st.spinner("Analyzing lecture material... Please wait."):
            if source_type == 'file':
                uploaded_file = source_val
                status_text.text("💾 Validating uploaded file...")
                progress_bar.progress(5)
                
                suffix = os.path.splitext(uploaded_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                    temp_file.write(uploaded_file.getbuffer())
                    file_path = temp_file.name
                
                lecture_title = uploaded_file.name
            else:
                youtube_url = source_val
                status_text.text("🔍 Validating YouTube URL...")
                progress_bar.progress(5)
                if not is_valid_youtube_url(youtube_url):
                    st.error("Invalid YouTube URL. Please enter a valid YouTube link.")
                    progress_bar.empty()
                    status_text.empty()
                    return
                
                status_text.text("📥 Downloading lecture audio (yt-dlp)...")
                progress_bar.progress(15)
                try:
                    file_path, lecture_title = download_youtube_audio(youtube_url)
                except Exception as e:
                    st.error(f"Failed to download YouTube video: {str(e)}. The video might be private, age-restricted, or unavailable.")
                    progress_bar.empty()
                    status_text.empty()
                    return
            
            # Store the uploaded file path in st.session_state
            st.session_state.uploaded_file_path = file_path

            # 1. Transcribe (Whisper)
            status_text.text("🎙️ Transcribing audio (faster-whisper)...")
            progress_bar.progress(40)
            transcript = whisper.transcribe(file_path)
            progress_bar.progress(70)

            # 2. Generate Structured Notes (Gemini)
            status_text.text("🧠 Generating structured study notes (Gemini)...")
            notes = llm.generate_notes(transcript)
            progress_bar.progress(90)

            # Save initial state to DB with 'notes_ready' status
            faiss_path = f"database/indexes/{int(time.time())}"
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lectures (title, file_path, status, transcript, notes, quiz, flashcards, faiss_path)
                VALUES (?, ?, ?, ?, ?, NULL, NULL, ?)
            """, (lecture_title, file_path, 'notes_ready', transcript, notes, faiss_path))
            lecture_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # Start background processing for long-running items (Quiz, Flashcards, FAISS Indexing)
            bg_thread = threading.Thread(
                target=run_background_pipeline,
                args=(lecture_id, transcript, faiss_path, st.session_state.gemini_api_key),
                daemon=True
            )
            bg_thread.start()

            progress_bar.progress(100)
            status_text.success("✅ Lecture notes ready! Redirecting to dashboard...")
            time.sleep(1) # Brief pause for user feedback
            
            # Store current lecture ID and navigate to Dashboard
            st.session_state.current_lecture_id = lecture_id
            st.session_state.navigation = "📚 My Lectures"
            st.rerun()

    except Exception as e:
        st.error(f"Error processing lecture: {str(e)}")
        status_text.error("Analysis failed.")
