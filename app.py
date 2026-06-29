import streamlit as st
from utils.helpers import load_css
from views import home, dashboard

# Page Configuration
st.set_page_config(
    page_title="Lumora | AI Lecture Intelligence",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom Styles
load_css("style.css")

# Initialize Session State
if "gemini_api_key" not in st.session_state:
    import os
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
    st.session_state.gemini_api_key = api_key

# Sidebar Navigation
st.sidebar.markdown("""
<div style='text-align: center; padding: 10px 0;'>
    <h1 style='color: #2563EB; font-size: 2rem; margin-bottom: 0;'>Lumora</h1>
    <p style='color: #64748B; font-size: 0.8rem;'>Intelligence Platform</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation Menu
menu_options = {
    "🏠 Home": home,
    "📚 My Lectures": dashboard,
}

menu_list = list(menu_options.keys())
if "navigation" not in st.session_state:
    st.session_state.navigation = "🏠 Home"

try:
    default_index = menu_list.index(st.session_state.navigation)
except ValueError:
    default_index = 0

selection = st.sidebar.radio("Navigation", menu_list, index=default_index, label_visibility="collapsed")
st.session_state.navigation = selection

st.sidebar.markdown("---")
if st.session_state.gemini_api_key:
    st.sidebar.markdown("<p style='color: #10B981; font-weight: 600; text-align: center;'>🟢 AI Engine Connected</p>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<p style='color: #EF4444; font-weight: 600; text-align: center;'>🔴 AI Engine Disconnected</p>", unsafe_allow_html=True)

# Routing Logic
if selection in menu_options:
    menu_options[selection].show()
