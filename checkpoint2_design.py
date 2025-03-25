# теперь функционал такой же как в painter.py

import streamlit as st
import base64

# Настройки страницы
st.set_page_config(
    page_title="ScaffoldMarkupTool",
    page_icon="✏️",
    layout="wide",
)

# 1) Инициализация переменных:

# Флаг: состояние боковой панели
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

# Переменная: для хранения загруженного файла
if "original_img" not in st.session_state:
    st.session_state.original_img = None

# Переменная: номер шага
if "step" not in st.session_state:
    st.session_state.step = 1

# Переменная: выбор режима
if 'mode' not in st.session_state:
    st.session_state.mode = "draw"

# 2) Инициализация функций

# Функция для скрытия/показа боковой панели
def toggle_sidebar():
    if st.session_state.sidebar_state == "expanded":
        st.session_state.sidebar_state = "collapsed"
    else:
        st.session_state.sidebar_state = "expanded"

# Функция для обработки кнопки "Next"
def next_step():
    if (st.session_state.step == 1 and st.session_state.original_img is None) or st.session_state.step == 3:
        return  # Выходим из функции
    else:
        st.session_state.step += 1

# Функция для обработки кнопки "Back"
def back_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1
        if st.session_state.step == 1:
            st.session_state.original_img = None

# Функция для обработки кнопки "Restart"
def restart():
    st.session_state.step = 1
    st.session_state.original_img = None

# 3) Боковая панель
if st.session_state.sidebar_state == "expanded":
    with st.sidebar:
        if st.session_state.step == 1:
            st.markdown("### Шаг 1: загрузка данных")

            # Загрузка изображения
            uploaded_file = st.file_uploader(
                "Выберите изображение", 
                type=["png", "jpg", "jpeg", "bmp", "gif", "tiff"] # добавить zip
            )

            # Если загружен файл - сохраняем его
            if uploaded_file is not None:
                st.session_state.original_img = uploaded_file # поменять логику под zip
                st.session_state.img = uploaded_file 

        elif st.session_state.step == 2:
            st.markdown("### Шаг 2: разметка изображений")

            # Вкладка "Tools"
            with st.expander("Tools", expanded=False):

                st.markdown("---")
                
                # Подраздел 1: выбор режима
                edit_container = st.container()
                with edit_container:
                    st.markdown("Mode:")

                    col1, col2 = st.columns([6, 3])
                    with col1:
                        mode_radio = st.radio(
                            'Mode',
                            ("Adding dots", "Editing dots"),
                            index=0 if st.session_state.mode == "draw" else 1, 
                            label_visibility="collapsed"
                        )
                        new_mode = "draw" if mode_radio == "Adding dots" else "edit"
                        if new_mode != st.session_state.mode:
                            st.session_state.mode = new_mode
                    with col2:
                        if st.button("Clear"):
                            pass


                # Разделитель
                st.markdown("---")

                # Подраздел 2: Zoom
                zoom_container = st.container()
                with zoom_container:
                    st.markdown("Zoom:")
                    col5, col6 = st.columns([6, 3])
                    with col5:
                        st.slider("Zoom", 0.15, 0.95, 0.5, 0.05, label_visibility="collapsed")
                    with col6:
                        st.button("Reset", key="zoom_reset", help="Zoom_reset")



                # Разделитель
                st.markdown("---")

                # Подраздел 3: настройка точек
                size_container = st.container()
                with size_container:
                    st.markdown("Dot settings:")
                    
                    col3, col4 = st.columns([6, 3])
                    with col3:
                        st.slider("Size", min_value=1, max_value=20, key="size_slider")
                    with col4:
                        st.session_state.current_point_color = st.color_picker(
                            "Color", 
                            key="color_picker"
                            )
                    


            # Кнопка-раздел "Save"
            with st.expander("Save", expanded=False):
                st.button("Markup image (png)", key="save_markup_image")
                st.button("Markup only (png)", key="save_markup_only")
                st.button("Points (json)", key="save_points_json")
                st.button("Project (zip)", key="save_project_zip")


        elif st.session_state.step == 3:
            st.markdown("### Шаг 3: воссоздание карты кластеров")

            # Кнопка-раздел "Tools"
            with st.expander("Tools", expanded=False):

                # Подраздел 1: Create map + кнопки ⚡ и ↑
                tool_container = st.container()
                with tool_container:
                    col1, col2, col3 = st.columns([5, 2, 2])
                    with col1:
                        st.button("Create map", key="create_map")
                    with col2:
                        st.button("⚡", key="fast_mode")
                    with col3:
                        st.button("↑", key="upload_map")

                # Разделитель
                st.markdown("---")

                # Подраздел 2: Zoom (аналогично шагу 2)
                zoom_container = st.container()
                with zoom_container:
                    col4, col5, col6, col7 = st.columns([4, 2, 2, 3])
                    with col4:
                        st.markdown("Zoom:")
                    with col5:
                        st.button("\uFF0B", key="zoom_in_3")
                    with col6:
                        st.button("\uFF0D", key="zoom_out_3")
                    with col7:
                        st.button("100", key="zoom_reset_3")

            # Кнопка-раздел "Save"
            with st.expander("Save", expanded=False):
                st.button("Mask (png)", key="save_mask_png")
                st.button("Mask+img (png)", key="save_mask_img_png")
                st.button("Morphological parameters", key="save_params")
                st.button("Area histogram", key="save_histogram")


        # Кнопки "Back", "Next" и "Restart"
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.button("Restart", on_click=restart, disabled=st.session_state.step == 1)
        with col2:
            st.button("Back", on_click=back_step, disabled=st.session_state.step == 1)
        with col3:
            st.button("Next", on_click=next_step, disabled=((st.session_state.step == 1 and st.session_state.original_img is None) or (st.session_state.step == 3)))

# 4) Основное окно

st.markdown(
    """
    <style>
    /* Отступы вокруг всего содержимого */
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
    if st.session_state.original_img is not None:
        # Конвертация загруженного изображения в base64
        def get_image_base64(image_file):
            return base64.b64encode(image_file.getvalue()).decode()

        encoded_image = get_image_base64(st.session_state.original_img)

        # Контейнер с отступами (20px) и прокруткой
        st.markdown(
            f"""
            <style>
            html, body, [data-testid="stApp"] {{
                height: 100%;
                margin: 0;
                padding: 0;
                overflow: hidden;
                box-sizing: border-box;
            }}
            .image-container {{
                width: calc(100vw - 20px);
                height: calc(100vh - 20px);
                padding: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                overflow: auto;
                border: 1px solid #ddd;
                box-sizing: border-box;
            }}
            .image-container img {{
                max-width: none;
                max-height: none;
            }}
            </style>
            <div class="image-container">
                <img src="data:image/png;base64,{encoded_image}" />
            </div>
            """,
            unsafe_allow_html=True
        )

elif st.session_state.step == 3:
    st.write("### Шаг 3")
