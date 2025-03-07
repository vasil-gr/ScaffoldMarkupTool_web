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

def toggle_sidebar():
    st.session_state.sidebar_state = "collapsed" if st.session_state.sidebar_state == "expanded" else "expanded"

def next_step():
    if (st.session_state.step == 1 and st.session_state.original_data is None) or st.session_state.step == 3:
        return
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
            st.markdown("### Шаг 1: Загрузка данных")
            uploaded_file = st.file_uploader(
                "Выберите изображение", 
                type=["png", "jpg", "jpeg", "bmp", "gif", "tiff"]
            )
            if uploaded_file is not None:
                st.session_state.original_data = uploaded_file

        elif st.session_state.step == 2:
            st.markdown("### Шаг 2: Разметка изображений")
            with st.expander("Tools", expanded=False):
                edit_container = st.container()
                with edit_container:
                    col1, col2, col3 = st.columns([4, 3, 3])
                    with col1:
                        st.markdown("Edit:")
                    with col2:
                        st.button("←", key="edit_left")
                    with col3:
                        st.button("→", key="edit_right")
                st.markdown("---")
                size_container = st.container()
                with size_container:
                    col4, col5 = st.columns([3, 7])
                    with col4:
                        st.markdown("Size:")
                    with col5:
                        st.slider("Размер", 1, 20, key="size_slider", label_visibility="collapsed")
                    col6, col7, col8, col9, col10 = st.columns([3, 2, 2, 2, 2])
                    with col6:
                        st.markdown("Color:")
                    with col7:
                        st.markdown('<button style="width:100%; height:30px; background-color:red; border:none; border-radius:5px;"> </button>', unsafe_allow_html=True)
                    with col8:
                        st.markdown('<button style="width:100%; height:30px; background-color:green; border:none; border-radius:5px;"> </button>', unsafe_allow_html=True)
                    with col9:
                        st.markdown('<button style="width:100%; height:30px; background-color:blue; border:none; border-radius:5px;"> </button>', unsafe_allow_html=True)
                    with col10:
                        st.markdown('<button style="width:100%; height:30px; background-color:black; border:none; border-radius:5px;"> </button>', unsafe_allow_html=True)
                st.markdown("---")
                zoom_container = st.container()
                with zoom_container:
                    col11, col12, col13, col14 = st.columns([4, 2, 2, 3])
                    with col11:
                        st.markdown("Zoom:")
                    with col12:
                        st.button("\uFF0B", key="zoom_in")
                    with col13:
                        st.button("\uFF0D", key="zoom_out")
                    with col14:
                        st.button("100", key="zoom_reset")
            with st.expander("Save", expanded=False):
                st.button("Markup image (png)", key="save_markup_image")
                st.button("Points (json)", key="save_points_json")

        elif st.session_state.step == 3:
            st.markdown("### Шаг 3: Воссоздание карты кластеров")
            with st.expander("Tools", expanded=False):
                tool_container = st.container()
                with tool_container:
                    col1, col2, col3 = st.columns([5, 2, 2])
                    with col1:
                        st.button("Create map", key="create_map")
                    with col2:
                        st.button("⚡", key="fast_mode")
                    with col3:
                        st.button("↑", key="upload_map")
                st.markdown("---")
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
            with st.expander("Save", expanded=False):
                st.button("Mask (png)", key="save_mask_png")
                st.button("Morphological parameters", key="save_params")

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
    .image-container {
        width: calc(100vw - 20px);
        height: calc(100vh - 20px);
        padding: 20px;
        overflow: auto;
        border: 1px solid #ddd;
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
        def get_image_base64(image_file):
            return base64.b64encode(image_file.getvalue()).decode()
        encoded_image = get_image_base64(st.session_state.original_data)
        st.markdown(
            f'<div class="image-container"><img src="data:image/png;base64,{encoded_image}" /></div>',
            unsafe_allow_html=True
        )

elif st.session_state.step == 3:
    st.write("### Шаг 3")