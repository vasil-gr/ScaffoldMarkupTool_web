import streamlit as st
from config.styles import setup_page_config, setup_step1_config

def help():
    setup_page_config("Help", "ℹ️")
    st.logo("media/logo.png", size = "large", icon_image=None)

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
    st.write("### Documentation: markup section")

    st.markdown("""
        The markup section is designed for working with cluster structures (e.g., scaffold surfaces). It helps researchers manually annotate crystallization centers on microimages and prepare data for subsequent analysis by generating cluster maps using a custom-built weighted Voronoi algorithm. The tool simplifies image-based structural work by combining interactive markup with advanced geometric modeling techniques.
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
            st.image("media/help_markup/markup_example.png", caption="Step 2: Markup", use_container_width=True)
        with col3:
            st.image("media/help_markup/claster_map_example.png", caption="Step 3: Cluster map", use_container_width=True)


    st.markdown("---")

    # --- Step 1: Upload ---
    st.markdown("##### 🔹 Step 1: Uploading data")

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

    with st.expander("📂 Show format examples"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Data unloading widget**")
            st.file_uploader(
                " ",
                type=["png", "jpg", "jpeg", "bmp", "gif", "tiff", "zip"]
            )
        with col2:
            st.write("**Single image exampl**")
            st.image("media/image_example.jpg", use_container_width=True)
        with col3:
            st.write("**Project ZIP contents**")
            st.code("""
                my_project.zip
                ├── image.png      # Unmarked image
                └── data.json      # Point coordinates & metadata
                        """)

    st.markdown("---")

    # --- Step 2: Markup ---
    st.markdown("##### 🔹 Step 2: Images marking")

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
            st.image("media/help_markup/save_examples/img+mark.png", use_container_width=True)
        with col2:
            st.write("**Markup only**")
            st.image("media/help_markup/save_examples/mark.png", use_container_width=True)
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
    st.markdown("##### 🔹 Step 3: Generation of cluster maps")

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
            st.image("media/help_markup/save_examples/img+map.png", use_container_width=True)
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

    with st.expander("📐 Show examples with bounding box"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Bbox_widget**")
            st.image("media/help_markup/bbox_widget.png", use_container_width=True)
        with col2:
            st.write("**Cluster map**")
            st.image("media/help_markup/claster_map_bbox_example.png", use_container_width=True)
        with col3:
            st.write("**Cluster areas json**")
            st.json({
                "image_name": "20x_w_0120.png",
                "image_size": {
                    "width": 2560,
                    "height": 1920
                },
                "bbox_size": {
                    "x_min": 100.0,
                    "y_min": 200.0,
                    "w": 1200.0,
                    "h": 1200.0
                },
                "areas": [
                    32191.60859824354,
                    29959.423286303052,
                    22430.62786609496,
                    83286.7920977276,
                    16410.840193910295,
                    41540.03215007363,
                    5393.922552288056,
                    37608.11793236862,
                    33777.611851511814,
                    24079.519725760114,
                    42884.803788354606,
                    19599.206385285128,
                    33566.607156017075,
                    45300.369797826046,
                    43361.697372422735,
                    83962.02754698755,
                    16487.448031399555,
                    19394.705623757218,
                    33573.791936263675,
                    6999.407835699832,
                    3935.367841483013,
                    54868.14342254933
                ],
                "areas_count": 22,
                "scale": {
                    "unit": "nanometers",
                    "value_per_pixel": None
                },
                "creation_date": "2025-04-07",
                "author": "user",
                "notes": None
                },
                expanded=1,
            )



def help_analysis():
    st.write("### Documentation: analysis section")

    st.markdown("""
        The analysis section is designed for processing and studying cluster data collected during the Markup stage. It allows users to upload one or multiple JSON datasets containing cluster area information and perform statistical analysis to extract key morphological parameters. The tool supports both single-image and batch processing, enabling researchers to explore distribution patterns, generate histograms, and compare structural characteristics across multiple samples.
        """)

    st.markdown("""
        The workflow consists of two main steps:  
        1. **Uploading** and verifying JSON datasets  
        2. **Analyzing** cluster areas and extracting morphological parameters
    """)


    st.markdown("---")

    # --- Step 1: Upload ---
    st.markdown("##### 🔹 Step 1: Uploading and validating data")

    st.markdown("""
    The first step involves uploading one or multiple JSON files containing pre-processed cluster area data.

    1. **File requirements**  
    - Each JSON file must include:
        - `"image_name"` — source image name
        - `"image_size"` — original image dimensions (width × height)
        - `"bbox_size"` — bounding box coordinates
        - `"areas"` — list of cluster areas

    2. **Validation checks**  
        - Files with missing fields or empty area lists are rejected.
        - If a dataset with the same name, image size, and bounding box parameters already exists, it is flagged as a duplicate.
        - If sizes differ, a new version is created automatically (e.g., `"image_name (1)"`).

    3. **Upload results**  
        - Successfully loaded files are displayed in a table with key properties.  
        - Problematic files are listed separately for review.

    The upload form is located in the sidebar and supports batch selection of multiple files at once.
    """)


    with st.expander("📂 Show JSON-file examples"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("**Valid JSON file**")
            st.json({
                "image_name": "20x_w_0155.jpg",
                "image_size": {
                    "width": 2560,
                    "height": 1920
                },
                "bbox_size": {
                    "x_min": 1060.0,
                    "y_min": 0.0,
                    "w": 1500.0,
                    "h": 1500.0
                },
                "areas": [
                    24201.878738429295,
                    121577.3628990552,
                    13011.955487032885
                ],
                "areas_count": 3,
                "scale": {
                    "unit": "nanometers",
                    "value_per_pixel": None
                },
                "creation_date": "2025-04-17",
                "author": "user",
                "notes": None
                },
                expanded=2,
            )
        with col2:
            st.write("**Non-duplicate (different bbox)**")
            st.json({
                "image_name": "20x_w_0155.jpg",
                "image_size": {
                    "width": 2560,
                    "height": 1920
                },
                "bbox_size": {
                    "x_min": 0.0,
                    "y_min": 420.0,
                    "w": 1500.0,
                    "h": 1500.0
                },
                "areas": [
                    49457.81,
                    118287.31,
                    115609.15
                ],
                "areas_count": 3,
                "scale": {
                    "unit": "nanometers",
                    "value_per_pixel": None
                },
                "creation_date": "2025-04-17",
                "author": "user",
                "notes": None
                },
                expanded=2,
            )
        with col3:
            st.write("**Duplicate (different areas list)**")
            st.json({
                "image_name": "20x_w_0155.jpg",
                "image_size": {
                    "width": 2560,
                    "height": 1920
                },
                "bbox_size": {
                    "x_min": 1060.0,
                    "y_min": 0.0,
                    "w": 1500.0,
                    "h": 1500.0
                },
                "areas": [
                    5459.09,
                    12410.12,
                    9117.40,
                    13011.96
                ],
                "areas_count": 4,
                "scale": {
                    "unit": "nanometers",
                    "value_per_pixel": None
                },
                "creation_date": "2025-04-17",
                "author": "user",
                "notes": None
                },
                expanded=2,
            )
    with st.expander("📥 Example of upload results"):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.image("media/help_analysis/uploading_example.png", use_container_width=True)


    st.markdown("---")

    # --- Step 2: Analysis ---
    st.markdown("##### 🔹 Step 2: Analysis of cluster areas")

    st.markdown("""
    After uploading the data, you can proceed to the analysis stage. The application offers two modes: visualization of area distributions through histograms and extraction of key morphological parameters. Settings and options are available in the sidebar. The results are displayed in the main workspace.

    1. **Mode Selection**
    - `"Histograms"` — explore the distribution of cluster areas  
    - `"Parameters"` — generate a table of morphological metrics

    2. **Histogram**
    - Double slider to set minimum and maximum visible cluster sizes (`"Range of areas"`)
    - Slider to control histogram granularity (`"Number of bins"`)
    - Histograms mode:
        - `"1 histogram"` — display a single histogram for a selected file or all files combined (`General`)  
        - `"2 histograms"` — overlay two histograms on the same plot for visual comparison
    - Data selection — choose a specific file or the combined dataset (`General`)  
    - The histogram is displayed along with a smoothed probability density curve (KDE).

    3. **Parameters**
    - Parameter selection — choose which metrics to display using checkboxes
    - Available parameters:
        - `"Number of complete clusters"` — total number of detected clusters  
        - `"Total area"` — sum of all cluster areas  
        - `"Cut-out area"` — image area minus total cluster area  
        - `"Mean area"` — average size of clusters  
        - `"Minimum area"` — smallest detected cluster  
        - `"Maximum area"` — largest detected cluster  
        - `"Standard deviation"` — spread of cluster areas
        - `"Coefficient of variation"` — relative standard deviation (dimensionless measure)
    - The first row ("General") shows combined statistics for all uploaded files. It summarizes the total number of clusters, overall area values, and variability measures across the entire dataset.
    """)

    with st.expander("📚 Show formulas for parameters"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('**Standard deviation (σ)**')
            st.latex(r"\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (x_i - \mu)^2}")
            st.markdown("Where:")
            st.markdown("""
            - N — number of clusters  
            - xᵢ — area of the i-th cluster  
            - μ — mean area of all clusters
            """)

        with col2:
            st.markdown('**Coefficient of variation (CV)**')
            st.latex(r"CV = \frac{\sigma}{\mu}")
            st.markdown("Where:")
            st.markdown("""
            - σ — standard deviation  
            - μ — mean area of all clusters
            """)

    with st.expander("📊 Show examples of results"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Parameters**")
            st.image("media/help_analysis/parameters_example.png", use_container_width=True)
        with col2:
            st.write("**Histograms**")
            st.image("media/help_analysis/histograms_example.png", use_container_width=True)




def help_start():
    st.write("### About app")

    st.markdown("""
    This application is designed to assist researchers in the morphological study of cluster structures, such as scaffold surfaces observed in microscopy images.  
    It combines two main functional modules:

    - **Markup** — enables users to manually annotate crystallization centers and generate weighted cluster maps based on Voronoi diagrams.
    - **Analysis** — provides tools for statistical evaluation of cluster areas, allowing for detailed distribution analysis and extraction of morphological parameters.

    Detailed instructions for working with each module are available on the corresponding help pages. You can switch between sections using the `"Select section"` widget in the sidebar.
    """)


# --- ВХОД ---
if __name__ == "__page__":
    help()