import streamlit as st

def setup_page_config():
    st.set_page_config(
        page_title="ScaffoldMarkupTool",
        page_icon="✏️",
        layout="wide",
    )
    st.markdown("""
    <style>
    hr {
        margin: 0.2rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def setup_step1_config():
    st.markdown(f"""
    <style>
    html, body, [data-testid="stApp"], .main, .block-container {{
        margin: 0 !important;
        padding-top: 35px;
        padding-left: 50px;
        max-width: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# делаем главное окно без границ и ограничений, если контент внутри вылазит за границы экрана по ширине или высоте, то появляются полосы прокрутки
def setup_step2_config():
    st.markdown(f"""
    <style>
    html, body, [data-testid="stApp"], .main, .block-container {{
        margin: 0 !important;
        padding: 0 !important;
        height: 100vh !important;
        max-width: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# размер холста вообще говоря не задаётся его содержимым (если холст меньше изображения - оно обрежится, если больше - будет свободное пространство)
# данная функция динамически адаптирвует размер холста под размер изображения
# поскольку холст - самый широкий объект в главном окне, то он и регулирует полосу прокрутки (если она вообще нужна)
def setup_step2_config_frame(width):
    st.markdown(f"""
    <style>
    iframe {{
        width: {width}px !important;
        display: block;
        border: none !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    </style>
    """, unsafe_allow_html=True)