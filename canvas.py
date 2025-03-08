import streamlit as st
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

# Load image
image_path = "20x_20_0070.jpg"
original_image = Image.open(image_path)
orig_width, orig_height = original_image.size

st.title("Image Annotation with Coordinates")

# Scale slider
scale_percent = st.slider("Image scale (%)", min_value=10, max_value=300, value=100, step=10)
scale_ratio = scale_percent / 100
new_size = (int(orig_width * scale_ratio), int(orig_height * scale_ratio))
resized_image = original_image.resize(new_size)

# Mode selection
if "mode" not in st.session_state:
    st.session_state.mode = 1

st.session_state.mode = st.radio("Select mode:", [1, 2], horizontal=True)

# Image container
with st.container(border=True):
    coords = streamlit_image_coordinates(resized_image, key="scrollable_img")

# Display coordinates
if coords:
    x_orig = int(coords["x"] / scale_ratio)
    y_orig = int(coords["y"] / scale_ratio)
    st.write(f"Original coordinates: ({x_orig}, {y_orig})")
    st.write(f"Mode: {st.session_state.mode}")
    st.write(f"Scale: {scale_percent}%")