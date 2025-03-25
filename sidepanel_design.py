import streamlit as st

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

if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"

if "original_img" not in st.session_state:
    st.session_state.original_img = None

if "step" not in st.session_state:
    st.session_state.step = 1

if 'mode' not in st.session_state:
    st.session_state.mode = "draw"

def toggle_sidebar():
    if st.session_state.sidebar_state == "expanded":
        st.session_state.sidebar_state = "collapsed"
    else:
        st.session_state.sidebar_state = "expanded"

def next_step():
    if (st.session_state.step == 1 and st.session_state.original_img is None) or st.session_state.step == 3:
        return
    else:
        st.session_state.step += 1

def back_step():
    if st.session_state.step > 1:
        st.session_state.step -= 1
        if st.session_state.step == 1:
            st.session_state.original_img = None

def restart():
    st.session_state.step = 1
    st.session_state.original_img = None

if st.session_state.sidebar_state == "expanded":
    with st.sidebar:
        if st.session_state.step == 1:
            st.markdown("""
            <h3 style='font-size: 18px; margin-bottom: 15px;'>
                Step 1: uploading data
            </h3>
            """, unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "**Choose an image**", 
                type=["png", "jpg", "jpeg", "bmp", "gif", "tiff"]
            )
            if uploaded_file is not None:
                st.session_state.original_img = uploaded_file
                st.session_state.img = uploaded_file 

        elif st.session_state.step == 2:
            st.markdown("""
            <h3 style='font-size: 18px; margin-bottom: 15px;'>
                Step 2: images marking
            </h3>
            """, unsafe_allow_html=True)
            with st.expander("**Tools**", expanded=False):
                st.markdown("---")
                edit_container = st.container()
                with edit_container:
                    st.markdown("**▸ Mode**")
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
                st.markdown("---")
                zoom_container = st.container()
                with zoom_container:
                    st.markdown("**▸ Zoom**")
                    col5, col6 = st.columns([6, 3])
                    with col5:
                        st.slider("Zoom", 0.15, 0.95, 0.5, 0.05, label_visibility="collapsed")
                    with col6:
                        st.button("Reset", key="zoom_reset", help="Zoom_reset")
                st.markdown("---")
                size_container = st.container()
                with size_container:
                    st.markdown("**▸ Dot settings**")
                    col3, col4 = st.columns([6, 3])
                    with col3:
                        st.slider("Size", min_value=1, max_value=20, key="size_slider")
                    with col4:
                        st.session_state.current_point_color = st.color_picker(
                            "Color", 
                            key="color_picker"
                            )
            with st.expander("**Save**", expanded=False):
                st.markdown("---")
                st.button("Markup image (png)", key="save_markup_image")
                st.button("Markup only (png)", key="save_markup_only")
                st.button("Points (json)", key="save_points_json")
                st.button("Project (zip)", key="save_project_zip")

        elif st.session_state.step == 3:
            st.markdown("""
            <h3 style='font-size: 18px; margin-bottom: 15px;'>
                Step 3: generation of cluster maps
            </h3>
            """, unsafe_allow_html=True)
            with st.expander("**Tools**", expanded=False):
                st.markdown("---")
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
                zoom_container = st.container()
                with zoom_container:
                    st.markdown("**▸ Zoom**")
                    col5, col6 = st.columns([6, 3])
                    with col5:
                        st.slider("Zoom", 0.15, 0.95, 0.5, 0.05, label_visibility="collapsed")
                    with col6:
                        st.button("Reset", key="zoom_reset", help="Zoom_reset")
            with st.expander("**Save**", expanded=False):
                st.button("Image (png)", key="save_img_png")
                st.button("Morphological parameters", key="save_params")
                st.button("Area histogram", key="save_histogram")

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.button("Restart", on_click=restart, disabled=st.session_state.step == 1)
        with col2:
            st.button("Back", on_click=back_step, disabled=st.session_state.step == 1)
        with col3:
            st.button("Next", on_click=next_step, disabled=((st.session_state.step == 1 and st.session_state.original_img is None) or (st.session_state.step == 3)))

if st.session_state.step == 1:
    st.write("### Шаг 1")

elif st.session_state.step == 2:
    st.write("### Шаг 2")

elif st.session_state.step == 3:
    st.write("### Шаг 3")