import streamlit as st
import streamlit as st
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

# --- Constants ---
IMAGE_PATH = "20x_20_0070.jpg"

# --- Page setup ---
st.set_page_config(layout="wide")

# --- Initialize session state ---
if "mode" not in st.session_state:
    st.session_state.mode = 1  # 1-add points, 2-remove points

if "scale_ratio" not in st.session_state:
    st.session_state.scale_ratio = 1

if "points" not in st.session_state:
    st.session_state.points = []  # Stores (x,y) coordinates

if "last_handled_coords" not in st.session_state:
    st.session_state.last_handled_coords = None  # Prevents duplicate clicks

if "radius" not in st.session_state:
    st.session_state.radius = 100  # Delete radius in pixels

# --- Draw points on scaled image ---
def draw_points_on_image(image, points, scale_ratio, point_radius=10, color=(255, 0, 0)):
    """Scale image and draw points on it"""
    img_width, img_height = image.size
    new_size = (int(img_width * scale_ratio), int(img_height * scale_ratio))
    image_resized = image.resize(new_size).convert("RGB")

    draw = ImageDraw.Draw(image_resized)
    for x, y in points:
        x_scaled = int(x * scale_ratio)
        y_scaled = int(y * scale_ratio)
        r = int(point_radius * scale_ratio)
        draw.ellipse([(x_scaled - r, y_scaled - r), (x_scaled + r, y_scaled + r)], fill=color)

    return image_resized

# --- UI Elements ---
st.radio("Select mode:", [1, 2], horizontal=True)  # Temporary spacer

scale_percent = st.slider(
    "Image scale (%)",
    min_value=10,
    max_value=300,
    value=int(st.session_state.scale_ratio*100),
    step=10,
    key="scale_slider"
)
st.session_state.scale_ratio = scale_percent / 100

st.session_state.mode = st.radio(
    "Select mode:", 
    [1, 2], 
    horizontal=True, 
    format_func=lambda x: "Add" if x == 1 else "Remove"
)

# --- Process image ---
image = Image.open(IMAGE_PATH)
img_width, img_height = image.size
resized_image = draw_points_on_image(image, st.session_state.points, st.session_state.scale_ratio)
resized_img_width, resized_img_height = resized_image.size

# --- CSS for responsive iframe ---
st.markdown(f"""
<style>
html, body, [data-testid="stApp"], .main, .block-container {{
    margin: 0 !important;
    padding: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    max-width: none !important;
    overflow-x: auto !important;
    overflow-y: auto !important;
}}
iframe {{
    width: {resized_img_width}px !important;
    height: {resized_img_height}px !important;
    display: block;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
}}
</style>
""", unsafe_allow_html=True)

# --- Handle click coordinates ---
coords = streamlit_image_coordinates(resized_image, key="click_img_with_scroll")

if coords and coords != st.session_state.last_handled_coords:
    st.session_state.last_handled_coords = coords
    x_orig = int(coords["x"] / st.session_state.scale_ratio)
    y_orig = int(coords["y"] / st.session_state.scale_ratio)

    # Add mode
    if st.session_state.mode == 1:
        st.session_state.points.append((x_orig, y_orig))
        st.rerun()
    # Remove mode
    elif st.session_state.mode == 2:
        radius = int(st.session_state.radius)
        if st.session_state.points:
            nearest_point = None
            nearest_dist_sq = radius ** 2 + 1
            for x, y in st.session_state.points:
                dist_sq = (x - x_orig) ** 2 + (y - y_orig) ** 2
                if dist_sq <= radius ** 2 and dist_sq < nearest_dist_sq:
                    nearest_dist_sq = dist_sq
                    nearest_point = (x, y)

            if nearest_point:
                st.session_state.points.remove(nearest_point)
                st.rerun()

# --- Display points list ---
st.write(f"📍 Total points: {len(st.session_state.points)}")
for i, (x, y) in enumerate(st.session_state.points, 1):
    st.write(f"{i}. ({x}, {y})")