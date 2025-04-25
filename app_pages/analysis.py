import streamlit as st
from config.styles import setup_page_config
from analysis_modules.step1_upload import render_upload_sidebar, render_upload_page
from analysis_modules.step2_result import render_result_sidebar, render_result_page
from config.session_manager import init_session_state_analysis_app, clear_session_state


# --- КОНТРОЛЬ НАВИГАЦИИ ----------------------------------------

def next_step_an():
    """Обработка кнопки Next"""
    if (st.session_state.step_an == 1 and len(st.session_state.data["image_names"]) > 0):
        st.session_state.step_an += 1
    else:
        return


def restart_an():
    """Обработка кнопки Restart"""
    st.session_state.step_an = 1
    clear_session_state("analysis") # полная очистка всех состояний
    init_session_state_analysis_app() # повторная инициализация



def analysis():
    """Точка входа в приложение"""
    setup_page_config("Analysis", "📈")
    init_session_state_analysis_app() # инициализация переменных

    st.logo("logo.png", size = "large", icon_image=None)
    
    # Боковая панель
    if st.session_state.sidebar_state == "expanded":
        # контент для каждого шага
        with st.sidebar: 
            if st.session_state.step_an == 1:
                render_upload_sidebar()
            elif st.session_state.step_an == 2:
                render_result_sidebar()
            
            # Общие кнопки навигации ("Next" и "Restart")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.button("Restart", on_click=restart_an, disabled=st.session_state.step_an == 1)
            with col2:
                st.button("Next", on_click=next_step_an, disabled=((st.session_state.step_an == 1 and len(st.session_state.data["image_names"]) == 0) or (st.session_state.step_an == 2)))

    # Основное окно
    if st.session_state.step_an == 1:
        render_upload_page()
    elif st.session_state.step_an == 2:
        render_result_page()


# --- ВХОД ---
if __name__ == "__page__":
    analysis()
