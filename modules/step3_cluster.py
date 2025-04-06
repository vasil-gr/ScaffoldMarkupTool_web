import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from shapely.geometry import Polygon, box

from config.styles import setup_step2and3_config, setup_step2and3_config_frame
from voronoi import weighted_voronoi as wv


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

        # Подраздел 1: Weight
        weight_container = st.container()
        with weight_container:
            st.markdown("**▸ Weight**")

            col1, col2 = st.columns([6, 3])
            with col1:
                new_weight = st.slider("Weight", st.session_state.min_scale, st.session_state.max_scale, st.session_state.scale, st.session_state.scale_step, label_visibility="collapsed")
                # if new_weight != st.session_state.weight:
                #    st.session_state.weight = new_weight
                #    st.rerun()
            with col2:
                if st.button("Reset", key="W_reset"):
                    pass
        
        st.markdown("---")

        # Подраздел 2: Zoom (аналогично как в шаге 2)
        zoom_container = st.container()
        with zoom_container:
            st.markdown("**▸ Zoom**")
            col3, col4 = st.columns([6, 3])
            with col3:
                new_scale = st.slider("Zoom", st.session_state.min_scale, st.session_state.max_scale, st.session_state.scale, st.session_state.scale_step, label_visibility="collapsed")
                if new_scale != st.session_state.scale:
                    st.session_state.scale = new_scale
                    st.rerun()
            with col4:
                # Сброс масштаба
                if st.button("Reset", key="zoom_reset", help="Zoom reset"):
                    new_scale = st.session_state.initial_scale
                    if new_scale != st.session_state.scale:
                        st.session_state.scale = new_scale
                        st.rerun()

        st.markdown("---")

        # Подраздел 3: Map settings
        tool_container = st.container()
        with tool_container:
            st.markdown("**▸ Map settings**")

            col5, col6 = st.columns([2, 2])
            with col5:
                # if st.session_state.step2_img_render:
                st.toggle("Img", True, key="show_img")
                st.toggle("Clasters", True, key="show_clasters")
                st.color_picker("Clasters", "#0000FF", key="current_claster_color")
            with col6:
                st.toggle("Dots", True, key="show_dots")
                st.toggle("Filling", False, key="show_filling", disabled=not st.session_state.get("show_clasters", True))
                st.color_picker("Filling", "#FFB300", key="current_filling_color")


    # Вкладка "Save"
    with st.expander("**Save**", expanded=False):
        st.button("Image (png)", key="save_img_png")
        st.button("Morphological parameters", key="save_params")
        st.button("Area histogram", key="save_histogram")


# --- RENDER: ОСНОВНОЕ ОКНО --------------------------------------

def render_cluster_page():
    """Основное окно для шага 3: кластеризация"""
    setup_step2and3_config()  # Настройка отступов и прокрутки

    # Создание изображения
    st.session_state.modified_img = create_modified_image()
    display_img = st.session_state.modified_img

    # Масштабирование изображения
    scaled_width = int(st.session_state.original_img.size[0] * st.session_state.scale)
    scaled_height = int(st.session_state.original_img.size[1] * st.session_state.scale)
    image_resized = display_img.resize((scaled_width, scaled_height)).convert("RGB")

    # Стили
    setup_step2and3_config_frame(scaled_width)

    # Получаем координаты от клика
    coords = streamlit_image_coordinates(image_resized, key="click_img_with_scroll")



    
    st.write(st.session_state.base_points)


    
# --- UTILS: НАСТРОЙКА ИЗОБРАЖЕНИЯ --------------------------------------

def create_modified_image():
    """Создает модифицированное изображение на основе текущих настроек"""
    img = st.session_state.original_img.copy()
    
    # Если Img выкл - серый фон
    if not st.session_state.get('show_img', True):
        gray_img = Image.new('RGB', img.size, (128, 128, 128))
        img = gray_img
    
    draw = ImageDraw.Draw(img)
    
    # Если Dots вкл - рисуем точки
    if st.session_state.get('show_dots', True):
        if st.session_state.base_points is not None:
            draw = ImageDraw.Draw(img)
            for point in st.session_state.base_points:
                x, y = point['x'], point['y']
                size = point['size']
                color = point['color']
                draw.ellipse(
                    [(x - size, y - size), (x + size, y + size)],
                    fill=color,
                    outline=color
                )
    
    # Если Map вкл - рисуем кластеры
    if st.session_state.get('show_clasters', True) and len(st.session_state.base_points)>0:

        # Весовая диаграмма Вороного
        width, height = st.session_state.original_img.size
        bbox = (0, 0, width, height)
        points = [(point['x'], point['y']) for point in st.session_state.base_points]
        weights = [point['weight'] for point in st.session_state.base_points]

        cells = wv.build_apollonius_polygons(points, weights)
        filtered_cells = filter_cells_outside_bbox(cells, bbox)

        # Рисуем многоугольники (ячейки) – линии синего цвета
        for cell in filtered_cells:
            poly = cell.boundary
            if not poly or len(poly) < 3:
                continue
            # Если многоугольник не замкнут, замыкаем его
            if poly[0] != poly[-1]:
                poly = poly + [poly[0]]
            # Рисуем линии по всем точкам
            draw.line(poly, fill=st.session_state.current_claster_color, width=3)
        
        # Рисуем подписи для точек с ненулевыми весами
        if weights is not None and len(weights) == len(points):
            try:
                m = int(width/80/2)
                font = ImageFont.truetype("arial.ttf", m*2)
            except:
                font = ImageFont.load_default()
            for (px, py), w in zip(points, weights):
                if abs(w) > 1e-9:
                    text = f"{w:+.2f}"
                    draw.text((px + m, py - m), text, fill="black", font=font)

    # Если Filling вкл - рисуем заливку
    if st.session_state.get('show_filling', True):
        pass
    
    return img



def filter_cells_outside_bbox(cells, bbox):
    """
    Обрезка диаграмы Вороного рамкой
    """
    result = []
    minx, miny, maxx, maxy = bbox
    clip_box = box(minx, miny, maxx, maxy)

    for cell in cells:
        poly_coords = cell.boundary
        if len(poly_coords) < 3:
            continue

        polygon = Polygon(poly_coords)
        if polygon.is_empty:
            continue

        # Crossing with a frame
        intersection = polygon.intersection(clip_box)
        if intersection.is_empty:
            continue
        if not intersection.equals(polygon):
            continue

        result.append(cell)

    return result