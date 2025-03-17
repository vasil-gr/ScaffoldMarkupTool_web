import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import math
import io
import os
import json
from datetime import datetime
import zipfile


# Настройки страницы и адаптивный стиль
st.set_page_config(layout="wide")


if 'original_img' not in st.session_state:
    st.session_state.original_img = None
    st.session_state.image_name = None


st.session_state.image_name = "20x_20_0070.jpg"
st.session_state.image_name = os.path.splitext(st.session_state.image_name)[0] # убираем расширение
st.session_state.original_img = Image.open("20x_20_0070.jpg")



# Параметры безопасного масштаба
DISPLAY_WIDTH = 1500
MAX_WIDTH = 2500
MIN_WIDTH = 300
STEP = 0.05

if 'display_width' not in st.session_state:
    st.session_state.display_width = DISPLAY_WIDTH
    st.session_state.max_width = MAX_WIDTH
    st.session_state.min_width = MIN_WIDTH
    st.session_state.scale_step = STEP


# Функция для расчета безопасного масштаба
def calculate_safe_scale(original_width):

    if original_width <= st.session_state.display_width:
        initial_scale = 1.0
    else:
        scale_factor = st.session_state.display_width / original_width
        initial_scale = math.floor(scale_factor / st.session_state.scale_step) * st.session_state.scale_step
        initial_scale = round(initial_scale, 2)

    min_scale_raw = st.session_state.min_width / original_width
    min_scale = math.ceil(min_scale_raw / st.session_state.scale_step) * st.session_state.scale_step
    min_scale = max(0.1, round(min_scale, 2))
    
    max_scale_raw = st.session_state.max_width / original_width
    max_scale_rounded_up = math.ceil(max_scale_raw / st.session_state.scale_step) * st.session_state.scale_step

    if (max_scale_rounded_up * original_width) <= st.session_state.max_width:
        max_scale = max_scale_rounded_up
    else:
        max_scale = math.floor(max_scale_raw / st.session_state.scale_step) * st.session_state.scale_step
    
    max_scale = min(3.0, round(max_scale, 2))
    
    initial_scale = max(min(initial_scale, max_scale), min_scale)
    
    return initial_scale, min_scale, max_scale


# Счётчик перерисовок (при нажатии кнопки - стереть все точки)
if 'redraw_id' not in st.session_state:
    st.session_state.redraw_id = 0


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
    width: {st.session_state.max_width}px !important;
    display: block;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
}}
</style>
""", unsafe_allow_html=True)


# Инициализация начального масштаба и пределов слайдера
if 'scale' not in st.session_state:
    initial_scale, min_scale, max_scale = calculate_safe_scale(st.session_state.original_img.size[0])
    st.session_state.scale = initial_scale
    st.session_state.initial_scale = initial_scale # понадобится для сброса масштаба
    st.session_state.min_scale = min_scale
    st.session_state.max_scale = max_scale

# Конфигурация
INITIAL_POINT_SIZE = 10
INITIAL_COLOR = "#FF0000"

# Инициализация переменных
if 'base_points' not in st.session_state:
    st.session_state.base_points = []
    st.session_state.canvas_data = None
    st.session_state.mode = "draw"
    st.session_state.current_point_size = INITIAL_POINT_SIZE
    st.session_state.current_point_color = INITIAL_COLOR

# Инициализация download_option - вариант скачивания на втором шаге
if 'download_option' not in st.session_state:
    st.session_state.download_option = None
    st.session_state.download_option_ind = None
    st.session_state.data_ready = False
    st.session_state.download_data = None


# Функции для сохранения

# Функция для добавление точек на изображение
def add_dots_to_image(new_image):
    """Наносит точки на изображение"""
    if st.session_state.base_points:  # рисуем точки только если они есть
        draw = ImageDraw.Draw(new_image)
        for point in st.session_state.base_points:
            x, y = point['x'], point['y']
            size = point['size']
            color = point['color']
            draw.ellipse(
                [(x - size, y - size), (x + size, y + size)],
                fill=color,
                outline=color
            )
    
    img_byte_arr = io.BytesIO()
    new_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

# Функция для создания изображения с разметкой
def create_marked_image():
    """Создает копию оригинального изображения с нанесенными точками"""
    new_image = st.session_state.original_img.copy()
    return add_dots_to_image(new_image)

# Функция для создания разметки на прозрачном фоне
def create_markup_only():
    """Создает изображение с точками на прозрачном фоне"""
    transparent_img = Image.new('RGBA', (st.session_state.original_img.size[0], st.session_state.original_img.size[1]), (0, 0, 0, 0))
    return add_dots_to_image(transparent_img)


# Функция для сохранения json файла с точками
def save_points():
    """Создаёт JSON-данные с информацией о точках"""
    points_data = {
        "image_name": st.session_state.image_name,
        "image_size": {
            "width": st.session_state.original_img.size[0],
            "height": st.session_state.original_img.size[1]
        },
        "points": st.session_state.base_points,
        "point_count": len(st.session_state.base_points),
        "scale": {
            "unit": "nanometers",
            "value_per_pixel": None
        },
        "creation_date": datetime.now().strftime("%Y-%m-%d"),
        "author": "user",
        "notes": None
    }
    
    json_str = json.dumps(points_data, indent=4)

    json_bytes = io.BytesIO(json_str.encode('utf-8'))
    json_bytes.seek(0)
    return json_bytes

    
# Функция для сохранения проекта (архив исходного изображения и json-файла с точками)
def save_project():
    """Создает ZIP-архив с исходным изображением и JSON-файлом точек"""

    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Добавляем исходное изображение
        img_byte_arr = io.BytesIO()
        st.session_state.original_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        zipf.writestr(f"{st.session_state.image_name}.png", img_byte_arr.getvalue())
        
        # 2. Добавляем JSON с точками
        json_data = save_points()
        zipf.writestr(f"{st.session_state.image_name}_points.json", json_data.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer






# Функции преобразования координат (не используется)
def scale_value(value, scale):
    """Масштабирование значения"""
    return value * scale

def get_scaled_points():
    """Возвращает масштабированные точки с их параметрами"""
    return [
        {
            'x': point['x'] * st.session_state.scale,
            'y': point['y'] * st.session_state.scale,
            'size': point['size'] * st.session_state.scale,
            'color': f"{point['color']}B3"
        }
        for point in st.session_state.base_points
    ]

# Генерация данных для холста
def generate_canvas_data():
    scaled_points = get_scaled_points()
    is_edit_mode = (st.session_state.mode == "edit")
    return {
        "version": "4.6.0",
        "objects": [
            {
                "type": "circle",
                "left": point['x'] - point['size'],
                "top": point['y'] - point['size'],
                "radius": point['size'],
                "fill": point['color'],
                "selectable": is_edit_mode,
                "hoverCursor": "move" if is_edit_mode else "default",
                "hasControls": is_edit_mode,
                "hasBorders": is_edit_mode,
                "lockRotation": True,
                "lockScalingX": True,
                "lockScalingY": True,
                "originX": "left",
                "originY": "top"
            }
            for point in scaled_points
        ]
    }

# Интерфейс
st.title("Масштабируемый холст с точками")

generate_canvas_data()

# Панель управления
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    new_scale = st.slider("Масштаб", st.session_state.min_scale, st.session_state.max_scale, st.session_state.scale, st.session_state.scale_step)
    if new_scale != st.session_state.scale:
        st.session_state.scale = new_scale
        st.session_state.canvas_data = generate_canvas_data()
    
    if st.button("Скинуть масштаб"):
        new_scale = st.session_state.initial_scale
        if new_scale != st.session_state.scale:
            st.session_state.scale = new_scale
            st.session_state.canvas_data = generate_canvas_data()
    
        
with col2:
    mode_radio = st.radio(
        "Режим",
        ("Добавление точек", "Редактирование точек"),
        index=0 if st.session_state.mode == "draw" else 1
    )
    new_mode = "draw" if mode_radio == "Добавление точек" else "edit"
    if new_mode != st.session_state.mode:
        st.session_state.mode = new_mode
        st.session_state.canvas_data = generate_canvas_data()
        
with col3:
    if st.button("Добавить точку (100,100)"):
        st.session_state.base_points.append({
            'x': 100,
            'y': 100,
            'size': st.session_state.current_point_size,
            'color': st.session_state.current_point_color
        })
        st.session_state.canvas_data = generate_canvas_data()
    
    if st.button("Очистить все точки", disabled=not st.session_state.base_points):
        st.session_state.base_points.clear()
        st.session_state.canvas_data = {"version": "4.6.0", "objects": []}
        st.session_state.redraw_id += 1
        

with col4:
    # Настройки для новых точек (не влияют на существующие)
    st.session_state.current_point_size = st.slider(
        "Размер точки", 
        min_value=1, 
        max_value=20, 
        value=st.session_state.current_point_size,
        key="size_slider"
    )
    
    st.session_state.current_point_color = st.color_picker(
        "Цвет точки", 
        st.session_state.current_point_color,
        key="color_picker"
    )

with col5:
    DOWNLOAD_CHOICES = ["Marked image (png)", "Markup only (png)", "Points data (json)", "Full Project (ZIP)"]
    
    # Выпадающий список
    selected_option = st.selectbox(
        "Select download option:",
        options=DOWNLOAD_CHOICES,
        index=st.session_state.download_option_ind,
        key='download_option_selector'
    )

    # Обновляем состояние при изменении выбора
    if selected_option != st.session_state.download_option:
        st.session_state.download_option = selected_option
        st.session_state.download_option_ind = DOWNLOAD_CHOICES.index(selected_option) if selected_option else None
        st.session_state.data_ready = False
        st.session_state.download_data = None

    # Конфигурация для каждого типа данных
    download_config = {
        "Marked image (png)": {
            "func": create_marked_image,
            "file_name": f"{st.session_state.image_name}_img+mark.png",
            "mime": "image/png"
        },
        "Markup only (png)": {
            "func": create_markup_only,
            "file_name": f"{st.session_state.image_name}_mark.png",
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
    if st.session_state.download_option and not st.session_state.data_ready:
        if st.button("Загрузить", key="load_button"):
            config = download_config[st.session_state.download_option]
            st.session_state.download_data = {
                "data": config["func"](),
                "file_name": config["file_name"],
                "mime": config["mime"]
            }
            st.session_state.data_ready = True
            st.rerun()

    # Кнопка "Скачать"
    if st.session_state.data_ready:
        data_info = st.session_state.download_data
        if st.download_button(
            label="Скачать",
            data=data_info["data"],
            file_name=data_info["file_name"],
            mime=data_info["mime"],
            key='download_button'
        ):
            # Сброс состояния после скачивания
            st.session_state.download_option = None
            st.session_state.download_option_ind = None
            st.session_state.data_ready = False
            st.session_state.download_data = None
            st.rerun()


# Масштабирование изображения
scaled_width = int(st.session_state.original_img.size[0] * st.session_state.scale)
scaled_height = int(st.session_state.original_img.size[1] * st.session_state.scale)

# Холст
canvas_result = st_canvas(
    fill_color=st.session_state.current_point_color + "B3",
    stroke_width=0,
    stroke_color=st.session_state.current_point_color + "B3",
    background_image=st.session_state.original_img,
    width=scaled_width,
    height=scaled_height,
    drawing_mode="point" if st.session_state.mode == "draw" else "transform",
    point_display_radius=st.session_state.current_point_size * st.session_state.scale if st.session_state.mode == "draw" else 0,
    initial_drawing=st.session_state.canvas_data,
    update_streamlit=True,
    key=f"canvas_{st.session_state.mode}_{st.session_state.scale}_{st.session_state.redraw_id}",
    display_toolbar=False
)

# Обработка изменений на холсте
if canvas_result.json_data is not None:
    new_objects = canvas_result.json_data.get("objects", [])
    
    new_base_points = []
    for obj in new_objects:
        if obj["type"] == "circle":
            center_x = obj["left"] + obj["radius"]
            if obj.get("originY") == "center":
                center_y = obj["top"]
            else:
                center_y = obj["top"] + obj["radius"]
            
            base_x = center_x / st.session_state.scale
            base_y = center_y / st.session_state.scale
            base_size = obj["radius"] / st.session_state.scale

            color = obj["fill"][:7] if obj["fill"].startswith('#') else "#FF0000"
            
            new_base_points.append({
                'x': base_x,
                'y': base_y,
                'size': base_size,
                'color': color
            })
    
    if new_base_points != st.session_state.base_points:
        st.session_state.base_points = new_base_points
        st.rerun()

# Отображение информации
st.subheader("Текущее состояние")
st.write(f"Масштаб: {st.session_state.scale}")
st.write("Текущий размер точки:", st.session_state.current_point_size)
st.write("Текущий цвет точки:", st.session_state.current_point_color)
st.write("Базовые точки:", st.session_state.base_points)