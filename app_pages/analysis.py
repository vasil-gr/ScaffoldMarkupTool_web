import streamlit as st
from config.styles import setup_page_config

def analysis():
    setup_page_config("Analysis", "📈")
    st.logo("logo.png", size = "large", icon_image=None)
    st.info("ℹ️ Please upload data using the sidebar")


# --- ВХОД ---
if __name__ == "__page__":
    analysis()
