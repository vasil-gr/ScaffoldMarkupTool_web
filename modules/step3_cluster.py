import streamlit as st
from PIL import Image, ImageDraw
import numpy as np

from config.styles import setup_step2and3_config, setup_step3_config_frame


# --- RENDER: БОКОВАЯ ПАНЕЛЬ --------------------------------------

def render_cluster_sidebar():
    """Боковая панель для шага 3: кластеризация"""
    st.markdown("""
    <h3 style='font-size: 18px; margin-bottom: 15px;'>
        Step 3: generation of cluster maps
    </h3>
    """, unsafe_allow_html=True)

    # Вкладка "Tools"
    with st.expander("**Tools**", expanded=False):

        st.markdown("---")

        # Подраздел 1: Map settings
        tool_container = st.container()
        with tool_container:
            st.markdown("**▸ Map settings**")

            st.select_slider(
                "Optimization of borders",
                options=["Base", "0.2", "0.4", "0.6", "0.8", "Optimal"], 
                label_visibility="collapsed"
            )

            col1, col2 = st.columns([2, 2])
            with col1:
                st.session_state.show_img = st.toggle("Img", st.session_state.show_img)
                st.session_state.show_map = st.toggle("Map", st.session_state.show_map)                      
            with col2:
                st.session_state.show_dots = st.toggle("Dots", st.session_state.show_dots)
                st.session_state.show_filling = st.toggle("Filling", st.session_state.show_filling, disabled=not st.session_state.show_map)

            if st.button("Create map", key="create_map"):
                st.session_state.modified_img = create_modified_image()
                st.rerun()

        st.markdown("---")

        # Подраздел 2: Zoom (аналогично как в шаге 2)
        zoom_container = st.container()
        with zoom_container:
            st.markdown("**▸ Zoom**")
            col5, col6 = st.columns([6, 3])
            with col5:
                new_scale = st.slider("Zoom", st.session_state.min_scale, st.session_state.max_scale, st.session_state.scale, st.session_state.scale_step, label_visibility="collapsed")
                if new_scale != st.session_state.scale:
                    st.session_state.scale = new_scale
                    st.rerun()
            with col6:
                # Сброс масштаба
                if st.button("Reset", key="zoom_reset", help="Zoom reset"):
                    new_scale = st.session_state.initial_scale
                    if new_scale != st.session_state.scale:
                        st.session_state.scale = new_scale

    # Вкладка "Save"
    with st.expander("**Save**", expanded=False):
        st.button("Image (png)", key="save_img_png")
        st.button("Morphological parameters", key="save_params")
        st.button("Area histogram", key="save_histogram")


# --- RENDER: ОСНОВНОЕ ОКНО --------------------------------------

def render_cluster_page():
    """Основное окно для шага 3: кластеризация"""
    setup_step2and3_config()  # Настройка отступов и прокрутки

    if st.session_state.step2_img_render:
        st.session_state.modified_img = create_modified_image()
        st.session_state.step2_img_render = False
    display_img = st.session_state.modified_img

    # Масштабирование изображения
    scaled_width = int(display_img.size[0] * st.session_state.scale)
    
    setup_step3_config_frame(scaled_width)  # фиксируем ширину контейнера
    
    # Контейнер с изображением (c динамической шириной)
    with st.container():
        st.image(display_img, width=scaled_width)
    
    st.write(st.session_state.base_points)




def create_modified_image():
    """Создает модифицированное изображение на основе текущих настроек"""
    img = st.session_state.original_img.copy()
    
    # Если Img выкл - серый фон
    if not st.session_state.get('show_img', True):
        gray_img = Image.new('RGB', img.size, (128, 128, 128))
        img = gray_img
    
    # Если Dots вкл - рисуем точки
    if st.session_state.get('show_dots', True):
        if st.session_state.base_points is not None:
            draw = ImageDraw.Draw(img)
            for point in st.session_state.base_points:
                x, y = point['x'], point['y']
                size = point['size']
                color = point['color']
                draw.ellipse(
                    [(x - size, y - size), (x + size, y + size)],
                    fill=color,
                    outline=color
                )
    
    # Если Map вкл - рисуем кластеры
    if st.session_state.get('show_map', True):
        pass

    # Если Filling вкл - рисуем заливку
    if st.session_state.get('show_filling', True):
        pass
    
    return img