import streamlit as st

def show():
    st.markdown("## ⚙️ Settings")

    st.markdown("""
    <div class="saas-card">
        <h3>Model Configuration</h3>
        <p class="secondary-text">Configure your AI model here.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.success("🟢 AI Engine Connected")
        st.info("The Gemini API key is securely managed by the application.")
        st.markdown("**Model:** Gemini 2.5 Flash")

    st.markdown("---")
    st.markdown("### 🛠️ Advanced Tools")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Clear Cache"):
            st.cache_resource.clear()
            st.toast("Cache cleared")

    with col2:
        if st.button("Download Data Export"):
            st.info("Export feature coming soon")