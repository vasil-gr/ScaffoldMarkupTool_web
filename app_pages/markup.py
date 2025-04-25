import streamlit as st

from config.session_manager import init_session_state_markup_app
from config.styles import setup_page_config
from markup_modules.step1_upload import render_upload_sidebar, render_upload_page
from markup_modules.step2_markup import render_markup_sidebar, render_markup_page
from markup_modules.step3_cluster import render_cluster_sidebar, render_cluster_page


# --- КОНТРОЛЬ НАВИГАЦИИ ----------------------------------------

def next_step():
    """Обработка кнопки Next"""
    if (st.session_state.step == 1 and st.session_state.original_img is None) or st.session_state.step == 3:
        return
    else:
        st.session_state.step += 1
        
        if st.session_state.step == 2 and not st.session_state.step2_img_render:
            # Если это первый рендер на шаге 2, то инициализируем данные точек, если их нет
            if st.session_state.base_points is None:
                st.session_state.base_points = []
            st.session_state.step2_img_render = True


def back_step():
    """Обработка кнопки Back"""
    if st.session_state.step == 3:
        st.session_state.step -= 1
        
        if st.session_state.step == 2:
            st.session_state.step2_initial_render = True

            # Если base_points нет, инициализируем пустой список
            if st.session_state.base_points is None:
                st.session_state.base_points = []


def restart():
    """Обработка кнопки Restart"""
    st.session_state.step = 1
    st.session_state.clear() # полная очистка всех состояний
    init_session_state_markup_app() # повторная инициализация


# --- ТОЧКА ВХОДА ------------------------------------------

def markup():
    """Точка входа в приложение"""
    setup_page_config("Markup", "✏️")
    init_session_state_markup_app() # инициализация переменных

    st.logo("logo.png", size = "large", icon_image=None)
    
    # Боковая панель
    if st.session_state.sidebar_state == "expanded":
        # контент для каждого шага
        with st.sidebar: 
            if st.session_state.step == 1:
                render_upload_sidebar()
            elif st.session_state.step == 2:
                render_markup_sidebar()
            elif st.session_state.step == 3:
                render_cluster_sidebar()
            
            # Общие кнопки навигации ("Back", "Next" и "Restart")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.button("Restart", on_click=restart, disabled=st.session_state.step == 1)
            with col2:
                st.button("Back", on_click=back_step, disabled=st.session_state.step != 3)
            with col3:
                st.button("Next", on_click=next_step, disabled=((st.session_state.step == 1 and st.session_state.original_img is None) or (st.session_state.step == 3)))

    # Основное окно
    if st.session_state.step == 1:
        render_upload_page()
    elif st.session_state.step == 2:
        render_markup_page()
    elif st.session_state.step == 3:
        render_cluster_page()


# --- ВХОД ---
if __name__ == "__page__":
    markup()