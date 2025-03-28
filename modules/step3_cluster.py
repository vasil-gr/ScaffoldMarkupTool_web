import streamlit as st


# --- RENDER: sidebar --------------------------------------

def render_cluster_sidebar():
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
                st.slider("Zoom", 0.15, 0.95, 0.5, 0.05, label_visibility="collapsed")
            with col6:
                st.button("Reset", key="zoom_reset", help="Zoom_reset")

    # Вкладка "Save"
    with st.expander("**Save**", expanded=False):
        st.button("Image (png)", key="save_img_png")
        st.button("Morphological parameters", key="save_params")
        st.button("Area histogram", key="save_histogram")


# --- RENDER: основное окно --------------------------------------

def render_cluster_page():
    st.write("### Step 3")