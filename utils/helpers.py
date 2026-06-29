import streamlit as st
import os

def load_css(file_name):
    """Loads a CSS file into the Streamlit app."""
    css_path = os.path.join("assets", "css", file_name)
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def apply_glassmorphism(content_func):
    """Decorator or wrapper to apply glassmorphism styling to a container."""
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    content_func()
    st.markdown('</div>', unsafe_allow_html=True)
