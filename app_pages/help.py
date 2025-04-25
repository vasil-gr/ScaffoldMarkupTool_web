import streamlit as st
from config.styles import setup_page_config, setup_step1_config

def help():
    setup_page_config("Help", "ℹ️")
    st.logo("logo.png", size = "large", icon_image=None)

    # Боковая панель
    if st.session_state.sidebar_state == "expanded":
        with st.sidebar: 
            
            # Варианты документации

            if st.session_state.section == "About app":
                index = 0
            elif st.session_state.section == "Markup section":
                index = 1
            elif st.session_state.section == "Analysis section":
                index = 2

            section = st.selectbox(
                "Select section:",
                options=["About app", "Markup section", "Analysis section"],
                index = index,
                key='section_option_selector'
            )

            # Обновляем состояние при изменении выбора
            if section != st.session_state.section:
                st.session_state.section = section


    # Основное окно
    setup_step1_config()

    if st.session_state.section == "About app":
        help_start()
    elif st.session_state.section == "Markup section":
        help_markup()
    elif st.session_state.section == "Analysis section":
        help_analysis()



# --- СТРАНИЦЫ ДОКУМЕНТАЦИИ ---

def help_markup():
    st.write("### Documentation: Markup section")

    st.markdown("""
        This application is designed for the morphological analysis of cluster structures (e.g., scaffold surfaces). It helps researchers manually annotate crystallization centers on microimages and generate cluster maps using a custom-built weighted Voronoi algorithm. The tool simplifies image-based structural analysis by combining interactive markup with advanced geometric modeling.
        """)
    
    st.markdown("""
        The workflow consists of three steps:  
        1. **Upload** an image or existing project  
        2. **Mark** crystallization centers manually  
        3. **Generate** and fine-tune the cluster map based on weights
        """)
    
    with st.expander("🚶 Show user journey visualization"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.image("media/image_example.jpg", caption="Step 1: Upload", use_container_width=True)
        with col2:
            st.image("media/markup_example.png", caption="Step 2: Markup", use_container_width=True)
        with col3:
            st.image("media/claster_map_example.png", caption="Step 3: Cluster map", use_container_width=True)


    st.markdown("---")

    # --- Step 1: Upload ---
    st.markdown("#### 🔹 Step 1: Uploading data")

    st.markdown("""
    This is where the user journey begins — by uploading an image or a previously saved project.

    1. **Single Image**  
    - Supported formats: PNG, JPG, JPEG, TIF, BMP, GIF  
    - Recommended resolution: 250–2500 px  
    - No preprocessing required  
    - Starts a new project with a blank markup canvas

    2. **Project Archive (ZIP)**  
    - Allows resuming work on an existing project  
    - Archive must contain:  
    - Exactly one unmarked PNG image  
        - One JSON file with saved markup data  
        - Opens the corresponding image with all annotated points  
    - Ideal for continuing annotation without losing progress

    The upload form is located in the sidebar.  
    You should upload **exactly one file** (either an image or a ZIP archive).
    """)

    with st.expander("📁 Show format examples"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Data unloading widget**")
            st.file_uploader(
                "",
                type=["png", "jpg", "jpeg", "bmp", "gif", "tiff", "zip"]
            )
        with col2:
            st.write("**Single image exampl**")
            st.image("media/image_example.jpg", width=300)
        with col3:
            st.write("**Project ZIP contents**")
            st.code("""
                my_project.zip
                ├── image.png      # Unmarked image
                └── data.json      # Point coordinates & metadata
                        """)

    st.markdown("---")

    # --- Step 2: Markup ---
    st.markdown("#### 🔹 Step 2: Images marking")

    st.markdown("""
    After uploading the image, you proceed to the markup stage. You can manually place reference points that represent crystallization centers. The interface supports two working modes: adding and editing points. All tools are located in the sidebar. The canvas with the image and interactive markup is displayed in the main area.

    1. **Mode selection**
    - `"Adding dots"` – click on the image to place new points  
    - `"Editing dots"` – drag points to move them, double-click to delete  
    - `"Clear"` – remove all points at once (cannot be undone)

    2. **Zoom controls**
    - Zoom slider – adjust the zoom level  
    - `"Reset"` – return to the default (optimal) zoom

    3. **Dot settings**
    - Select color of the dots
    - Select size of the dots

    4. **Saving options**
    - `"Marked image (png)"` – image with visible dots  
    - `"Markup only (png)"` – dots only, on transparent background  
    - `"Points data (json)"` – contains coordinates, size, color, weight, metadata  
    - `"Full Project (ZIP)"` – full archive (can be reloaded on Step 1)
    """)

    with st.expander("💾 Show save examples"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("**Marked image**")
            st.image("media/save_examples/img+mark.png", width=300)
        with col2:
            st.write("**Markup only**")
            st.image("media/save_examples/mark.png", width=300)
        with col3:
            st.write("**Points data**")
            st.json({
                "image_name": "20x_w_0120.png",
                "image_size": {
                    "width": 2560,
                    "height": 1920
                },
                "points": [
                    {
                        "x": 35.0,
                        "y": 300.0,
                        "weight": 0.0,
                        "size": 10.0,
                        "color": "#FF0000"
                    },
                    {
                        "x": 787.5,
                        "y": 87.5,
                        "weight": -80.0,
                        "size": 10.0,
                        "color": "#FF0000"
                    }
                ],
                "point_count": 117,
                "scale": {
                    "unit": "nanometers",
                    "value_per_pixel": None
                },
                "creation_date": "2025-04-25",
                "author": "user",
                "notes": None
                },
                expanded=1,
            )
        with col4:
            st.write("**Full Project**")
            st.code("""
                my_project.zip
                ├── image.png      # Unmarked image
                └── data.json      # Point coordinates & metadata
                        """)

    st.markdown("---")

    # --- Step 3: Cluster Map ---
    st.markdown("#### 🔹 Step 3: Generation of cluster maps")

    st.markdown("""
    After annotation, the application automatically generates a cluster map based on the marked points. By default, a classic Voronoi diagram is used: each pixel is assigned to the nearest point. However, each point also has a weight, which affects the cluster boundaries. When weights are non-zero, the system switches to a weighted Voronoi diagram. The calculation is performed using a custom C++ library, wrapped for Python [🧩](https://github.com/vasil-gr/WeightedVoronoi-CGAL).
    The cluster map is displayed on the canvas. Tools and export options are available in the sidebar.

    1. **Weight Controls**
    - `"Set exact weight"` – use a slider to assign an exact value  
    - `"Increment by value"` – enter a number to add to the current weight  
    - `"Reset"` – reset all weights to zero  
    - To apply weight: click near a point (within 100 px) — the closest one will be updated

    2. **Zoom Controls**
    - Zoom slider – adjust the zoom level  
    - `"Reset"` – return to default scale

    3. **Map Settings**
    - `"Img"` – toggle image visibility  
    - `"Dots"` – toggle point visibility  
    - `"Clusters"` – toggle cluster boundaries  
    - `"Filling"` – toggle cluster fill  
    - Customize boundar and fill color for clusters

    4. **Bounding Box**
    - Define analysis frame with:  
        - `X min`, `Y min`, `W`, `H`  
    - The box trims clusters that go beyond it  
    - Default size matches the full image

    5. **Saving Options**
    - `"Cluster map (png)"` – current visual state of the canvas  
    - `"Cluster areas (json)"` – cluster areas, bounding box, metadata  
    - `"Points data (json)"` – contains coordinates, size, color, weight, metadata 
    - `"Full Project (ZIP)"` – full archive (can be reloaded on Step 1)
    """)

    with st.expander("💾 Show save examples"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write("**Cluster map**")
            st.image("media/save_examples/img+map.png", width=300)
        with col2:
            st.write("**Cluster areas**")
            st.json({
                "image_name": "20x_w_0120.png",
                "image_size": {
                    "width": 2560,
                    "height": 1920
                },
                "bbox_size": {
                    "x_min": 0.0,
                    "y_min": 0.0,
                    "w": 2560.0,
                    "h": 1920.0
                },
                "areas": [
                    23710.48670332395,
                    32191.60859824354,
                    21762.679632701176,
                    31316.60063932637,
                    66864.32923886478
                ],
                "areas_count": 5,
                "scale": {
                    "unit": "nanometers",
                    "value_per_pixel": None
                },
                "creation_date": "2025-04-25",
                "author": "user",
                "notes": None
            },
                expanded=1,
            )
        with col3:
            st.write("**Points data**")
            st.json({
                "image_name": "20x_w_0120.png",
                "image_size": {
                    "width": 2560,
                    "height": 1920
                },
                "points": [
                    {
                        "x": 35.0,
                        "y": 300.0,
                        "weight": 0.0,
                        "size": 10.0,
                        "color": "#FF0000"
                    },
                    {
                        "x": 787.5,
                        "y": 87.5,
                        "weight": -80.0,
                        "size": 10.0,
                        "color": "#FF0000"
                    }
                ],
                "point_count": 117,
                "scale": {
                    "unit": "nanometers",
                    "value_per_pixel": None
                },
                "creation_date": "2025-04-25",
                "author": "user",
                "notes": None
                },
                expanded=1,
            )
        with col4:
            st.write("**Full Project**")
            st.code("""
                my_project.zip
                ├── image.png      # Unmarked image
                └── data.json      # Point coordinates & metadata
                        """)


    st.markdown("---")

def help_analysis():
    st.markdown("## 📘 How to use the analysis application")

def help_start():
    st.markdown("## 📘 Select the section on the side panel")


# --- ВХОД ---
if __name__ == "__page__":
    help()