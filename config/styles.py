import streamlit as st


# --- ОБЩАЯ НАСТРОЙКА СТРАНИЦЫ ---------------------------------------

def setup_page_config(title, icon):
    """Настройка глобальных параметров страницы"""
    st.set_page_config(
        page_title= title,
        page_icon= icon,
        layout="wide",
    )

    # дополнительный стиль - уменьшение отступов
    st.markdown("""
    <style>
    hr {
        margin: 0.2rem 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- НАСТРОЙКА ДЛЯ ШАГА 1 (ЗАГРУЗКА) -------------------------------

def setup_step1_config():
    """Настройка для шага 1 (загрузка): отступы и ширина страницы"""
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


# --- НАСТРОЙКА ДЛЯ ШАГА 2 и 3 (РАЗМЕТКА и КЛАСТЕРИЗАЦИЯ) -------------------------------

def setup_step2and3_config():
    """Настройка для шага 2 (разметка): отступы, ширина страницы, полосы прокрутки при необходимости"""
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


def setup_step2and3_config_frame(width):
    """Устанавливает ширину холста (iframe) динамически под размер изображения.
    Так как холст - основной объект по ширине, то он определяет необходимость горизонтальной прокрутки.
    """
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

