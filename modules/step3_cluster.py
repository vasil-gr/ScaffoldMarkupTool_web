import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import io
import json
import os
from datetime import datetime
from shapely.geometry import Polygon, box

from config.styles import setup_step2and3_config, setup_step2and3_config_frame
from modules.step2_markup import save_points, save_project
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

            # Выбор режима редактирования веса
            st.session_state.mode_3 = st.radio(
                "Choose editing mode",
                ["Set exact weight", "Increment by value"],
                horizontal=True, 
                label_visibility="collapsed"
            )


            col1, col2 = st.columns([6, 3])
            with col1:
                if st.session_state.mode_3 == "Set exact weight":
                    new_weight = st.slider("Weight", st.session_state.min_weight, st.session_state.max_weight, st.session_state.weight, st.session_state.weight_step, label_visibility="collapsed")
                    if new_weight != st.session_state.weight:
                        st.session_state.weight = new_weight
                        st.rerun()
                if st.session_state.mode_3 == "Increment by value":
                    st.number_input("Weight", min_value=-100.0, max_value=100.0, value=st.session_state.plas_weight, step=st.session_state.weight_step, key="plas_weight", label_visibility="collapsed")


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

    # Вкладка "Bounding box"
    with st.expander("**Bounding box**", expanded=False):
        box_container = st.container()
        with box_container:  

            width, height = map(float, st.session_state.original_img.size)

            col7, col8 = st.columns([2, 2])
            with col7:
                new_box_x_min = st.number_input("X min", min_value=0.0, max_value=width, value=st.session_state.box_x_min, step=50.0)
                if new_box_x_min != st.session_state.box_x_min:
                    st.session_state.box_x_min = new_box_x_min
                    st.rerun()

                new_box_y_min = st.number_input("Y min", min_value=0.0, max_value=height, value=st.session_state.box_y_min, step=50.0)
                if new_box_y_min != st.session_state.box_y_min:
                    st.session_state.box_y_min = new_box_y_min
                    st.rerun()
                
            with col8:

                new_box_w = st.number_input("W", min_value=0.0, max_value=width, value=st.session_state.box_w, step=50.0)
                if new_box_w != st.session_state.box_w:
                    st.session_state.box_w = new_box_w
                    st.rerun()

                new_box_h = st.number_input("H", min_value=0.0, max_value=height, value=st.session_state.box_h, step=50.0)
                if new_box_h != st.session_state.box_h:
                    st.session_state.box_h = new_box_h
                    st.rerun()

    # Вкладка "Save"
    with st.expander("**Save**", expanded=False):
        DOWNLOAD_CHOICES = ["Claster map (png)", "Claster areas (json)", "Points data (json)", "Full Project (ZIP)"]

        # Варианты сохранения
        selected_option_3 = st.selectbox(
            "Select download option:",
            options=DOWNLOAD_CHOICES,
            index=st.session_state.download_option_ind_3,
            key='download_option_selector_3'
        )

        # Обновляем состояние при изменении выбора
        if selected_option_3 != st.session_state.download_option_3:
            st.session_state.download_option_3 = selected_option_3
            st.session_state.download_option_ind_3 = DOWNLOAD_CHOICES.index(selected_option_3) if selected_option_3 else None
            st.session_state.data_ready_3 = False
            st.session_state.download_data_3 = None

        # Конфигурация для каждого типа данных
        download_config_3 = {
            "Claster map (png)": {
                "func": save_claster_map,
                "file_name": f"{os.path.splitext(st.session_state.image_name)[0]}_map.png",
                "mime": "image/png"
            },
            "Claster areas (json)": {
                "func": save_areas,
                "file_name": f"{os.path.splitext(st.session_state.image_name)[0]}_areas.json",
                "mime": "image/png"
            },
            "Points data (json)": {
                "func": save_points,
                "file_name": f"{os.path.splitext(st.session_state.image_name)[0]}_points.json",
                "mime": "application/json"
            },
            "Full Project (ZIP)": {
                "func": save_project,
                "file_name": f"{os.path.splitext(st.session_state.image_name)[0]}_project.zip",
                "mime": "application/zip"
            }
        }

        # Кнопка "Загрузить"
        if st.session_state.download_option_3 and not st.session_state.data_ready_3:
            if st.button("Prepare", key="load_button"):
                config = download_config_3[st.session_state.download_option_3]
                st.session_state.download_data_3 = {
                    "data": config["func"](),
                    "file_name": config["file_name"],
                    "mime": config["mime"]
                }
                st.session_state.data_ready_3 = True
                st.rerun()

        # Кнопка "Скачать"
        if st.session_state.data_ready_3:
            data_info = st.session_state.download_data_3
            if st.download_button(
                label="Download",
                data=data_info["data"],
                file_name=data_info["file_name"],
                mime=data_info["mime"],
                key='download_button'
            ):
                # Сброс состояния после скачивания
                st.session_state.download_option_3 = None
                st.session_state.download_option_ind_3 = None
                st.session_state.data_ready_3 = False
                st.session_state.download_data_3 = None
                st.rerun()






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

    # Обработка кликов: только если coords новые и впервые в этом рендере (если этого не сделать, то при каждом рендере будет снова обрабатываться клик)
    if coords and coords != st.session_state.last_handled_coords:
        # Сохраняем, что эти coords уже отработаны (сохраняем до учёта масштаба)
        st.session_state.last_handled_coords = coords

        # учёт масштаба
        x_orig = int(coords["x"] / st.session_state.scale)
        y_orig = int(coords["y"] / st.session_state.scale)

        # Найдём ближайшую точку в радиусе
        radius = 100
        if st.session_state.base_points:
            nearest_point = None
            nearest_dist_sq = radius ** 2 + 1  # чуть больше максимума
            for point in st.session_state.base_points:
                # Извлекаем координаты и проверяем расстояние
                x, y = point['x'], point['y']
                dist_sq = (x - x_orig) ** 2 + (y - y_orig) ** 2
                if dist_sq <= radius ** 2 and dist_sq < nearest_dist_sq:
                    nearest_dist_sq = dist_sq
                    nearest_point = point

            # Если нашли, присвоим ей вес
            if nearest_point:
                if st.session_state.mode_3 == "Set exact weight":
                    nearest_point['weight'] = st.session_state.weight
                    st.rerun()
                elif st.session_state.mode_3 == "Increment by value":
                    nearest_point['weight'] += st.session_state.plas_weight
                    st.rerun()                 


    
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
    if st.session_state.get('show_clasters', True) and st.session_state.base_points is not None:

        # Весовая диаграмма Вороного
        width, _ = st.session_state.original_img.size

        bbox = (st.session_state.box_x_min, 
                st.session_state.box_y_min, 
                st.session_state.box_x_min + st.session_state.box_w, 
                st.session_state.box_y_min + st.session_state.box_h)
        
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

        # Рисуем пунктирную рамку bbox — прямоугольник с границами


        def draw_dashed_line(start, end):
            """Рисует пунктир от start до end"""
            dash = 10  # длина одного штриха
            gap = 5    # длина пробела между штрихами
            color = "black"
            width = 2


            total_len = ((end[0]-start[0])**2 + (end[1]-start[1])**2)**0.5
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            direction = (dx / total_len, dy / total_len)
            n = int(total_len // (dash + gap))
            for i in range(n + 1):
                x0 = start[0] + (dash + gap) * i * direction[0]
                y0 = start[1] + (dash + gap) * i * direction[1]
                x1 = x0 + dash * direction[0]
                y1 = y0 + dash * direction[1]
                if (x1 - start[0])**2 + (y1 - start[1])**2 <= total_len**2:
                    draw.line([(x0, y0), (x1, y1)], fill=color, width=width)

        # Четыре стороны bbox
        draw_dashed_line((bbox[0], bbox[1]), (bbox[2], bbox[1]))  # верх
        draw_dashed_line((bbox[2], bbox[1]), (bbox[2], bbox[3]))  # правый
        draw_dashed_line((bbox[2], bbox[3]), (bbox[0], bbox[3]))  # низ
        draw_dashed_line((bbox[0], bbox[3]), (bbox[0], bbox[1]))  # левый




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



# --- UTILS: ФУНКЦИИ ДЛЯ СОХРАНЕНИЯ --------------------------------------

def save_claster_map():
    """Создание изображения с разметкой"""
    new_image = st.session_state.modified_img.copy()

    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr



def compute_cell_areas():
    """Вычисляет площади для всех ячеек на основе их границ (boundary)"""
    # Весовая диаграмма Вороного
    width, height = st.session_state.original_img.size
    
    bbox = (st.session_state.box_x_min, 
            st.session_state.box_y_min, 
            st.session_state.box_x_min + st.session_state.box_w, 
            st.session_state.box_y_min + st.session_state.box_h)
    
    points = [(point['x'], point['y']) for point in st.session_state.base_points]
    weights = [point['weight'] for point in st.session_state.base_points]

    cells = wv.build_apollonius_polygons(points, weights)
    filtered_cells = filter_cells_outside_bbox(cells, bbox)

    areas = []
    for cell in filtered_cells:
        poly_coords = cell.boundary
        if len(poly_coords) < 3:
            continue  # not a polygon
        polygon = Polygon(poly_coords)
        if polygon.is_valid and not polygon.is_empty:
            areas.append(polygon.area)
    return areas

def save_areas():
    """Создание JSON-файла с площадями кластеров и морфологическими параметрами"""

    cell_areas = compute_cell_areas()

    points_data = {
        "image_name": st.session_state.image_name,
        "image_size": {
            "width": st.session_state.original_img.size[0],
            "height": st.session_state.original_img.size[1]
        },
        "bbox_size": {
            "x_min": st.session_state.box_x_min,
            "y_min": st.session_state.box_y_min,
            "w": st.session_state.box_w,
            "h": st.session_state.box_h,
        },
        "areas": cell_areas,
        "areas_count": len(cell_areas),
        "scale": {
            "unit": "nanometers",
            "value_per_pixel": None  # ! можно добавить настройки
        },
        "creation_date": datetime.now().strftime("%Y-%m-%d"),
        "author": "user",  # ! можно добавить настройки
        "notes": None  # ! можно добавить настройки
    }
    
    json_str = json.dumps(points_data, indent=4) # конвертация в JSON строку
    json_bytes = io.BytesIO(json_str.encode('utf-8'))
    json_bytes.seek(0)
    return json_bytes