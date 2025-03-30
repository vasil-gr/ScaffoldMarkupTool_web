import streamlit as st
import zipfile
import io
from PIL import Image
import json
import os

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

if "image_name" not in st.session_state:
    st.session_state.image_name = None

if "base_points" not in st.session_state:
    st.session_state.base_points = None

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

def restart():
    st.session_state.step = 1
    st.session_state.original_img = None
    st.session_state.base_points = None

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
                type=["png", "jpg", "jpeg", "bmp", "gif", "tiff", "zip"]
            )

            def validate_zip_contents(zip_file):
                with zipfile.ZipFile(zip_file) as z:
                    file_list = z.namelist()
                    png_files = [f for f in file_list if f.lower().endswith('.png')]
                    json_files = [f for f in file_list if f.lower().endswith('.json')]
                    return len(png_files) == 1 and len(json_files) == 1

            def extract_image_from_zip(zip_file):
                with zipfile.ZipFile(zip_file) as z:
                    file_list = z.namelist()
                    png_file = next(f for f in file_list if f.lower().endswith('.png'))
                    with z.open(png_file) as f:
                        return Image.open(f).convert("RGB"), os.path.basename(png_file)
            
            def load_points_from_json(zip_file):
                with zipfile.ZipFile(zip_file) as z:
                    json_files = [f for f in z.namelist() if f.lower().endswith('.json')]
                    if not json_files:
                        return None
                    
                    json_file = json_files[0]
                    with z.open(json_file) as f:
                        try:
                            json_data = json.load(f)
                        except json.JSONDecodeError:
                            return None
                    
                    if not all(key in json_data for key in ['image_name', 'points']):
                        return None
                    
                    valid_points = []
                    for point in json_data['points']:
                        if not all(k in point for k in ['x', 'y', 'size', 'color']):
                            continue
                        
                        try:
                            valid_points.append({
                                'x': float(point['x']),
                                'y': float(point['y']),
                                'size': float(point['size']),
                                'color': point['color']
                            })
                        except (ValueError, TypeError):
                            continue
                    
                    return valid_points

            if uploaded_file is not None:
                if uploaded_file.type == "application/zip" or uploaded_file.name.endswith('.zip'):
                    try:
                        if validate_zip_contents(uploaded_file): 
                            img, img_name = extract_image_from_zip(uploaded_file) 
                            st.session_state.original_img = img
                            st.session_state.image_name = img_name
                            points = load_points_from_json(uploaded_file)
                            if points:
                                st.session_state.base_points = points
                        else:
                            st.error("Zip archive must contain exactly one PNG image and one JSON file")
                    except Exception as e:
                        st.error(f"Error processing zip file: {str(e)}") 
                else:
                    try:
                        img = Image.open(uploaded_file).convert("RGB")
                        st.session_state.original_img = img
                        st.session_state.image_name = uploaded_file.name
                    except Exception as e:
                        st.error(f"Error processing image: {str(e)}")

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
    st.write("### Step 1: Data Upload")
    st.write("Here you can read how to work in the program: Help")
    
    if st.session_state.get('original_img'):
        if st.session_state.base_points is not None:
            st.success(f"✅ Image and {len(st.session_state.base_points)} points from archive successfully uploaded!")
        else:
            st.success("✅ Image successfully uploaded!")
        st.image(st.session_state.original_img, caption="Uploaded Image")
    else:
        st.info("ℹ️ Please upload data using the sidebar")
        st.markdown("""
        #### You can upload:
        1. **Single Image**  
        - Formats: PNG, JPG, JPEG, BMP, GIF, TIFF  
        - Recommended size: 250-2500 px (larger images will be compressed)  
        - Starts a new project with blank markup

        2. **Project Archive (ZIP)**  
        - Must contain:  
            - Exactly one PNG image (unmarked)  
            - One JSON file with point data  
        - Opens existing project with:  
            - The corresponding image  
            - Pre-filled markup points  
        - Allows continuing previous work
        """)
        with st.expander("Show format examples"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Single Image Example**")
                st.image("20x_20_0070.jpg", width=150)
            with col2:
                st.write("**Project ZIP Contents**")
                st.code("""
        my_project.zip
        ├── image.png      # Unmarked image
        └── data.json      # Point coordinates & metadata
                """)

elif st.session_state.step == 2:
    st.write("### Шаг 2")

elif st.session_state.step == 3:
    st.write("### Шаг 3")
