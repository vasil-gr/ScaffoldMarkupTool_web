import streamlit as st

from config.session_manager import init_session_state
from config.styles import setup_page_config
from modules.step1_upload import render_sidebar_step1, render_step1
from modules.step2_markup import render_markup_sidebar, render_markup_page


# Функция для обработки кнопки "Next"
def next_step():
    if (st.session_state.step == 1 and st.session_state.original_img is None) or st.session_state.step == 3:
        return
    else:
        st.session_state.step += 1

# Функция для обработки кнопки "Back"
def back_step():
    if st.session_state.step == 2: # когда нужно: пользователь загружает проект с точками, шаг 1 -> шаг 2 -> шаг 1 -> шаг 2 -> точки должны перерисовываться
        st.session_state.step2_initial_render = True
    if st.session_state.step > 1:
        st.session_state.step -= 1

# Функция для обработки кнопки "Restart"
def restart():
    st.session_state.step = 1
    st.session_state.clear() # полная очистка всех состояний
    init_session_state() # повторная инициализация



def main():

    # css и пр
    setup_page_config()
    # инициализация переменных
    init_session_state()
    
    # Боковая панель
    if st.session_state.sidebar_state == "expanded":
                
        with st.sidebar:
            
            # Контент для каждого шага
            if st.session_state.step == 1:
                render_sidebar_step1()
            elif st.session_state.step == 2:
                render_markup_sidebar()
            elif st.session_state.step == 3:
                pass
            
            # Общие кнопки навигации ("Back", "Next" и "Restart")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                st.button("Restart", on_click=restart, disabled=st.session_state.step == 1)
            with col2:
                st.button("Back", on_click=back_step, disabled=st.session_state.step == 1)
            with col3:
                st.button("Next", on_click=next_step, disabled=((st.session_state.step == 1 and st.session_state.original_img is None) or (st.session_state.step == 3)))

    
    # Основное окно для каждого шага
    if st.session_state.step == 1:
        render_step1()
    elif st.session_state.step == 2:
        render_markup_sidebar()
    elif st.session_state.step == 3:
        pass

if __name__ == "__main__":
    main()