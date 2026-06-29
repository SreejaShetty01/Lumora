import streamlit as st

def show():
    st.markdown("## ⚙️ Settings")

    st.success("🟢 AI Engine Connected")

    st.info("The Gemini API key is securely managed by the application.")

    st.markdown("**Model:** Gemini 2.5 Flash")

    st.markdown("---")

    st.markdown("### 🛠️ Advanced Tools")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear Cache"):
            st.cache_resource.clear()
            st.success("Cache cleared successfully!")

    with col2:
        if st.button("Download Data Export"):
            st.info("Export feature coming soon.")