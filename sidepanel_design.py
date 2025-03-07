import streamlit as st
import base64

st.set_page_config(
    page_title="ScaffoldMarkupTool",
    page_icon="✏️",
    layout="wide",
)

if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

if "original_data" not in st.session_state:
    st.session_state.original_data = None

if "step" not in st.session_state:
    st.session_state.step = 1

def next_step():
    if (st.session_state.step == 1 and st.session_state.original_data is None) or st.session_state.step == 3:
        return
    else:
        st.session_state.step += 1

def back_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1
        if st.session_state.step == 1:
            st.session_state.original_data = None

def restart():
    st.session_state.step = 1
    st.session_state.original_data = None

if st.session_state.sidebar_state == "expanded":
    with st.sidebar:
        if st.session_state.step == 1:
            st.markdown("### Шаг 1: загрузка данных")
            uploaded_file = st.file_uploader("Выберите изображение", type=["png", "jpg"])
            if uploaded_file is not None:
                st.session_state.original_data = uploaded_file

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.button("Restart", on_click=restart, disabled=st.session_state.step == 1)
        with col2:
            st.button("Back", on_click=back_step, disabled=st.session_state.step == 1)
        with col3:
            st.button("Next", on_click=next_step, disabled=((st.session_state.step == 1 and st.session_state.original_data is None) or (st.session_state.step == 3)))

st.markdown(
    """
    <style>
    .block-container {
        padding: 40px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if st.session_state.step == 1:
    st.markdown("## Scaffold Markup Tool")
    st.write("Приложение ScaffoldMarkupTool предназначено для разметки микрофотографий скаффолдов.")

elif st.session_state.step == 2:
    if st.session_state.original_data is not None:
        # Конвертация в base64
        def get_image_base64(image_file):
            return base64.b64encode(image_file.getvalue()).decode()

        encoded_image = get_image_base64(st.session_state.original_data)

        # Контейнер с прокруткой
        st.markdown(
            f"""
            <style>
            .image-container {{
                width: calc(100vw - 20px);
                height: calc(100vh - 20px);
                padding: 20px;
                overflow: auto;
                border: 1px solid #ddd;
            }}
            </style>
            <div class="image-container">
                <img src="data:image/png;base64,{encoded_image}" />
            </div>
            """,
            unsafe_allow_html=True
        )