import streamlit as st
from config.styles import setup_page_config

def help():
    setup_page_config("Help", "ℹ️")
    st.logo("logo.png", size = "large", icon_image=None)
    st.markdown("How to use the application")


# --- ВХОД ---
if __name__ == "__page__":
    help()