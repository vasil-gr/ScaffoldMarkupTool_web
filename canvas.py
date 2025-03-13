import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import math


# Настройки страницы и адаптивный стиль
st.set_page_config(layout="wide")

image = Image.open("20x_20_0070.jpg")
original_width, original_height = image.size



# Параметры безопасного масштаба
DISPLAY_WIDTH = 1500  # Оптимальная ширина для начального отображения
MAX_WIDTH = 2500      # Максимальная ширина при увеличении
MIN_WIDTH = 300       # Минимальная ширина при уменьшении
STEP = 0.05           # Шаг изменения масштаба

# Функция для расчета безопасного масштаба
def calculate_safe_scale(original_width):
    # Стартовый масштаб
    if original_width <= DISPLAY_WIDTH:
        initial_scale = 1.0
    else:
        scale_factor = DISPLAY_WIDTH / original_width
        initial_scale = math.floor(scale_factor / STEP) * STEP
        initial_scale = round(initial_scale, 2)
    
    # Минимальный масштаб
    min_scale_raw = MIN_WIDTH / original_width
    min_scale = math.ceil(min_scale_raw / STEP) * STEP
    min_scale = max(0.1, round(min_scale, 2))
    
    # Максимальный масштаб
    max_scale_raw = MAX_WIDTH / original_width
    max_scale_rounded_up = math.ceil(max_scale_raw / STEP) * STEP
    if (max_scale_rounded_up * original_width) <= MAX_WIDTH:
        max_scale = max_scale_rounded_up
    else:
        max_scale = math.floor(max_scale_raw / STEP) * STEP
    
    max_scale = min(3.0, round(max_scale, 2))
    
    # initial_scale находится в границах
    initial_scale = max(min(initial_scale, max_scale), min_scale)
    
    return initial_scale, min_scale, max_scale

initial_scale, min_scale, max_scale = calculate_safe_scale(original_width)



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
    width: {MAX_WIDTH}px !important;
    display: block;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
}}
</style>
""", unsafe_allow_html=True)




# Конфигурация
INITIAL_SCALE = initial_scale
INITIAL_POINT_SIZE = 10
INITIAL_COLOR = "#FF0000"

# Инициализация переменных
if 'scale' not in st.session_state:
    st.session_state.scale = INITIAL_SCALE
    st.session_state.base_points = []
    st.session_state.canvas_data = None
    st.session_state.mode = "draw"
    st.session_state.current_point_size = INITIAL_POINT_SIZE
    st.session_state.current_point_color = INITIAL_COLOR
    

# Функции преобразования координат
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

# Панель управления
col1, col2, col3, col4 = st.columns(4)
with col1:
    new_scale = st.slider("Масштаб", min_scale, max_scale, st.session_state.scale, STEP)
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
        st.session_state.base_points = []
        st.session_state.canvas_data = {"version": "4.6.0", "objects": []}

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

# Масштабирование изображения
scaled_width = int(original_width * new_scale)
scaled_height = int(original_height * new_scale)

# Холст
canvas_result = st_canvas(
    fill_color=st.session_state.current_point_color + "B3",
    stroke_width=0,
    stroke_color=st.session_state.current_point_color + "B3",
    background_image=image,
    width=scaled_width,
    height=scaled_height,
    drawing_mode="point" if st.session_state.mode == "draw" else "transform",
    point_display_radius=st.session_state.current_point_size * st.session_state.scale if st.session_state.mode == "draw" else 0,
    initial_drawing=st.session_state.canvas_data,
    update_streamlit=True,
    key=f"canvas_{st.session_state.mode}_{st.session_state.scale}",
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