import streamlit as st
import os

def show():
    # Lazy imports to optimize startup speed
    from database.manager import DatabaseManager
    from pipeline.llm_engine import LLMEngine
    import sqlite3

    db = DatabaseManager()
    
    # Selection of lecture (accept done or notes_ready status)
    conn = db.get_connection()
    lectures = conn.execute("SELECT id, title FROM lectures WHERE status IN ('done', 'notes_ready') ORDER BY created_at DESC").fetchall()
    conn.close()

    if not lectures:
        st.info("👋 No lectures processed yet. Go to the Home page to get started!")
        return

    lecture_titles = {l[1]: l[0] for l in lectures}
    
    # Check if we have a current lecture in session state
    current_idx = 0
    if "current_lecture_id" in st.session_state:
        for idx, (title, id) in enumerate(lecture_titles.items()):
            if id == st.session_state.current_lecture_id:
                current_idx = idx
                break

    selected_title = st.selectbox("Select Lecture", list(lecture_titles.keys()), index=current_idx)
    lecture_id = lecture_titles[selected_title]
    st.session_state.current_lecture_id = lecture_id

    # Fetch lecture details using sqlite3.Row for name-based lookup
    conn = db.get_connection()
    conn.row_factory = sqlite3.Row
    lecture = conn.execute("SELECT * FROM lectures WHERE id=?", (lecture_id,)).fetchone()
    
    # Fetch chat history
    history_rows = conn.execute("SELECT role, content FROM chat_history WHERE lecture_id=? ORDER BY timestamp ASC", (lecture_id,)).fetchall()
    conn.close()

    chat_history = [{"role": r, "content": c} for r, c in history_rows]

    # Layout
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Notes", 
        "💬 AI Chat", 
        "🧠 Quiz", 
        "🃏 Flashcards", 
        "📊 Knowledge Graph", 
        "📜 Transcript"
    ])

    with tab1:
        st.markdown(lecture['notes'])

    with tab2:
        # Check if FAISS index is built
        faiss_path = lecture['faiss_path']
        if faiss_path and os.path.exists(f"{faiss_path}.index"):
            display_chat_interface(lecture_id, lecture['transcript'], chat_history)
        else:
            st.info("⚡ AI Chat is building the semantic knowledge base in the background. It will be ready in a minute!")
            if st.button("🔄 Refresh Chat"):
                st.rerun()

    with tab3:
        if lecture['quiz']:
            render_quiz(lecture_id, lecture['quiz'])
        elif lecture['status'] == 'failed':
            st.error("Failed to generate quiz.")
        else:
            st.info("🧠 AI Quiz is being generated in the background. Please wait a moment...")
            if st.button("🔄 Refresh Quiz"):
                st.rerun()

    with tab4:
        if lecture['flashcards']:
            render_flashcards(lecture['flashcards'])
        elif lecture['status'] == 'failed':
            st.error("Failed to generate flashcards.")
        else:
            st.info("🃏 Flashcards are being generated in the background. Please wait a moment...")
            if st.button("🔄 Refresh Flashcards"):
                st.rerun()

    with tab5:
        st.markdown("""
        <div class="saas-card" style="text-align: center; padding: 40px 20px;">
            <div style="font-size: 3rem; margin-bottom: 15px;">📊</div>
            <h3>Knowledge Graph Visualizer</h3>
            <p class="secondary-text" style="max-width: 500px; margin: 0 auto; color: #64748B;">
                Interactive mapping of key lecture concepts, relationships, and cognitive connections is coming in the next release.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with tab6:
        st.markdown(f"""
        <div class="saas-card" style="max-height: 500px; overflow-y: auto;">
            {lecture['transcript']}
        </div>
        """, unsafe_allow_html=True)

def clean_json_string(json_str):
    if not json_str:
        return ""
    cleaned = json_str.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.find("\n")
        if first_newline != -1:
            cleaned = cleaned[first_newline:].strip()
        else:
            cleaned = cleaned[3:].strip()
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()
    return cleaned

def parse_quiz_json(quiz_json):
    import json
    import logging
    cleaned = clean_json_string(quiz_json)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logging.error(f"Quiz JSON parsing failed. Error: {str(e)}. Raw content: {quiz_json}")
        try:
            data = json.loads(cleaned.strip())
        except Exception:
            raise e
            
    if isinstance(data, dict):
        if "questions" in data:
            return data["questions"]
        for val in data.values():
            if isinstance(val, list):
                return val
        return [data]
    elif isinstance(data, list):
        return data
    return []

def render_quiz(lecture_id, quiz_json):
    try:
        quiz_data = parse_quiz_json(quiz_json)
        st.markdown("### 🧠 Interactive Lecture Quiz")
        st.caption("Select your answer for each question to see instant feedback and explanations.")
        
        for idx, q in enumerate(quiz_data):
            st.markdown(f"**Question {idx+1}:** {q['question']}")
            options = q['options']
            option_labels = [f"{chr(65+i)}) {opt}" for i, opt in enumerate(options)]
            
            key = f"quiz_{lecture_id}_{idx}"
            selected = st.radio("Choose an option:", option_labels, key=key, index=None)
            
            if selected:
                chosen_letter = selected[0]
                correct_letter = q['answer'].upper()
                
                if chosen_letter == correct_letter:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Incorrect. The correct answer is {correct_letter}.")
                
                st.info(f"**Explanation:** {q['explanation']}")
            st.markdown("---")
    except Exception as e:
        st.error("Failed to parse quiz format.")
        st.caption(f"Error details: {str(e)}")
        st.write(quiz_json)

def render_flashcards(flashcards_json):
    import json
    import logging
    try:
        cleaned = clean_json_string(flashcards_json)
        try:
            flashcards_data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logging.error(f"Flashcards JSON parsing failed. Error: {str(e)}. Raw content: {flashcards_json}")
            try:
                flashcards_data = json.loads(cleaned.strip())
            except Exception:
                raise e
                
        st.markdown("### 🃏 Key Concepts Flashcards")
        st.caption("Expand each card below to see the definition/explanation.")
        
        for idx, card in enumerate(flashcards_data):
            with st.expander(f"🃏 {card['term']}"):
                st.markdown(f"**Definition:**  \n{card['definition']}")
    except Exception as e:
        st.error("Failed to parse flashcards format.")
        st.caption(f"Error details: {str(e)}")
        st.write(flashcards_json)

def display_chat_interface(lecture_id, transcript, chat_history):
    st.markdown("### Chat with Lecture")
    
    # Display history
    for msg in chat_history:
        role_class = "chat-user" if msg["role"] == "user" else "chat-bot"
        st.markdown(f"""
        <div class="chat-bubble {role_class}">
            <strong>{'You' if msg['role'] == 'user' else 'Lumora'}:</strong><br>
            {msg['content']}
        </div>
        """, unsafe_allow_html=True)

    # Input
    if query := st.chat_input("Ask a question about this lecture..."):
        if not st.session_state.gemini_api_key:
            st.error("Connect API Key in Settings to chat.")
            return

        # Show user message immediately
        st.markdown(f"""
        <div class="chat-bubble chat-user">
            <strong>You:</strong><br>{query}
        </div>
        """, unsafe_allow_html=True)

        with st.spinner("Thinking..."):
            from database.manager import DatabaseManager
            from pipeline.llm_engine import LLMEngine
            from pipeline.rag_engine import RAGEngine
            import sqlite3

            db = DatabaseManager()
            llm = LLMEngine(st.session_state.gemini_api_key)
            rag = RAGEngine()
            
            # 1. Get context from RAG
            conn = db.get_connection()
            lecture = conn.execute("SELECT faiss_path FROM lectures WHERE id=?", (lecture_id,)).fetchone()
            conn.close()
            
            context = rag.query(query, lecture[0])
            
            # 2. Generate response
            response = llm.chat_with_context(query, context, chat_history[-5:]) # Last 5 for context
            
            # 3. Save to DB
            conn = db.get_connection()
            conn.execute("INSERT INTO chat_history (lecture_id, role, content) VALUES (?, ?, ?)", (lecture_id, 'user', query))
            conn.execute("INSERT INTO chat_history (lecture_id, role, content) VALUES (?, ?, ?)", (lecture_id, 'assistant', response))
            conn.commit()
            conn.close()
            
            st.rerun()
