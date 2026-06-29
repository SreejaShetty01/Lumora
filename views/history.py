import streamlit as st
from database.manager import DatabaseManager

def show():
    st.markdown("## 📜 Lecture History")
    st.markdown("<p class='secondary-text'>Access all your previously processed lectures and their insights.</p>", unsafe_allow_html=True)

    db = DatabaseManager()
    conn = db.get_connection()
    lectures = conn.execute("SELECT id, title, created_at, status FROM lectures ORDER BY created_at DESC").fetchall()
    conn.close()

    if not lectures:
        st.info("No lectures found.")
        return

    for lecture in lectures:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.markdown(f"**{lecture[1]}**")
                st.caption(f"Processed on: {lecture[2]}")
            with col2:
                status_color = "#10B981" if lecture[3] == "done" else "#F59E0B"
                st.markdown(f"<span style='color: {status_color}; font-weight: 600;'>{lecture[3].upper()}</span>", unsafe_allow_html=True)
            with col3:
                if st.button("View", key=f"view_{lecture[0]}"):
                    st.session_state.current_lecture_id = lecture[0]
                    st.session_state.navigation = "Dashboard" # Note: navigation is handled by radio, might need a hack or st.rerun
                    st.info("Switching to Dashboard...")
                    st.rerun()
            st.markdown("---")
