import streamlit as st

def show():
    st.markdown("## ⚙️ GEMINI TEST PAGE")
    
    st.markdown("""
    <div class="saas-card">
        <h3>Model Configuration</h3>
        <p class="secondary-text">Configure your AI model and API credentials here.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        api_key = st.text_input("Gemini API Key", value=st.session_state.get("gemini_api_key", ""), type="password")
        model = st.selectbox("Gemini Model", ["gemini-2.5-flash", "gemini-2.5-pro"])
        
        if st.button("Save Settings"):
            st.session_state.gemini_api_key = api_key
            st.success("Settings saved successfully!")
            st.rerun()

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
