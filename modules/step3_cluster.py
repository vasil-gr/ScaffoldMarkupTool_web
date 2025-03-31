import streamlit as st

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
                st.toggle("Img")
                st.toggle("Map")                        
            with col2:
                st.toggle("Dots")
                st.toggle("Filling")  

            st.button("Create map", key="create_map")

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

    # Масштабирование изображения
    scaled_width = int(st.session_state.original_img.size[0] * st.session_state.scale)
    
    setup_step3_config_frame(scaled_width)  # фиксируем ширину контейнера
    
    # Контейнер с изображением (c динамической шириной)
    with st.container():
        st.image(st.session_state.original_img, width=scaled_width)
    
    st.write(st.session_state.base_points)