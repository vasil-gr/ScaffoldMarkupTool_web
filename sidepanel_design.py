import streamlit as st
import base64

# Page config
st.set_page_config(
    page_title="ScaffoldMarkupTool",
    page_icon="✏️",
    layout="wide",
)

# 1) Initialize session state
if "sidebar_state" not in st.session_state:
    st.session_state.sidebar_state = "expanded"
if "original_data" not in st.session_state:
    st.session_state.original_data = None
if "step" not in st.session_state:
    st.session_state.step = 1

# 2) Navigation functions
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

# 3) Sidebar
if st.session_state.sidebar_state == "expanded":
    with st.sidebar:
        if st.session_state.step == 1:
            st.markdown("### Step 1: Upload Data")
            uploaded_file = st.file_uploader(
                "Choose an image", 
                type=["png", "jpg", "jpeg"]
            )
            if uploaded_file is not None:
                st.session_state.original_data = uploaded_file

        elif st.session_state.step == 2:
            st.markdown("### Step 2: Image Markup")

            # Tools expander
            with st.expander("Tools", expanded=False):
                # Edit tools
                edit_container = st.container()
                with edit_container:
                    col1, col2, col3 = st.columns([4, 3, 3])
                    with col1:
                        st.markdown("Edit:")
                    with col2:
                        st.button("←", key="edit_left", help="Remove dot")
                    with col3:
                        st.button("→", key="edit_right", help="Restore dot")
                st.markdown("---")

                # Size & Color
                size_container = st.container()
                with size_container:
                    col4, col5 = st.columns([3, 7])
                    with col4:
                        st.markdown("Size:")
                    with col5:
                        st.slider("Size", 1, 20, key="size_slider", label_visibility="collapsed")

                    col6, col7, col8, col9, col10 = st.columns([3, 2, 2, 2, 2])
                    with col6:
                        st.markdown("Color:")
                    with col7:
                        st.button("", key="color_red", help="Red")
                    with col8:
                        st.button("", key="color_green", help="Green")
                    with col9:
                        st.button("", key="color_blue", help="Blue")
                    with col10:
                        st.button("", key="color_black", help="Black")
                st.markdown("---")

                # Zoom controls
                zoom_container = st.container()
                with zoom_container:
                    col11, col12, col13, col14 = st.columns([4, 2, 2, 3])
                    with col11:
                        st.markdown("Zoom:")
                    with col12:
                        st.button("+", key="zoom_in")
                    with col13:
                        st.button("-", key="zoom_out")
                    with col14:
                        st.button("100%", key="zoom_reset")

            # Save options
            with st.expander("Save", expanded=False):
                st.button("Markup image (PNG)", key="save_png")
                st.button("Points (JSON)", key="save_json")

        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.button("Restart", on_click=restart, disabled=st.session_state.step == 1)
        with col2:
            st.button("Back", on_click=back_step, disabled=st.session_state.step == 1)
        with col3:
            st.button("Next", on_click=next_step, disabled=((st.session_state.step == 1 and st.session_state.original_data is None) or (st.session_state.step == 3)))

# 4) Main window
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
    st.write("Upload an image to begin markup.")

elif st.session_state.step == 2:
    if st.session_state.original_data is not None:
        def get_image_base64(image_file):
            return base64.b64encode(image_file.getvalue()).decode()
        encoded_image = get_image_base64(st.session_state.original_data)
        st.markdown(
            f'<div class="image-container"><img src="data:image/png;base64,{encoded_image}" /></div>',
            unsafe_allow_html=True
        )