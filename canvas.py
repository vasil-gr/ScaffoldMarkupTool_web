import streamlit as st
from streamlit_drawable_canvas import st_canvas
import json

# Конфигурация
BASE_WIDTH, BASE_HEIGHT = 600, 400
INITIAL_SCALE = 1.0
INITIAL_POINT_SIZE = 10
INITIAL_COLOR = "#FF0000"

# Инициализация переменных
if 'scale' not in st.session_state:
    st.session_state.scale = INITIAL_SCALE
    st.session_state.base_points = []  # словари: {'x', 'y', 'size', 'color'}
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
            'color': f"{point['color']}B3"  # фиксированная прозрачность 0.7 (B3 в hex)
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
    new_scale = st.slider("Масштаб", 0.1, 3.0, st.session_state.scale, 0.1)
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

# Холст
canvas_result = st_canvas(
    fill_color=st.session_state.current_point_color + "B3",  # прозрачность
    stroke_width=0,
    stroke_color=st.session_state.current_point_color + "B3",
    background_color="#fff",
    height=BASE_HEIGHT,
    width=BASE_WIDTH,
    drawing_mode="point" if st.session_state.mode == "draw" else "transform",
    point_display_radius=st.session_state.current_point_size * st.session_state.scale if st.session_state.mode == "draw" else 0,
    initial_drawing=st.session_state.canvas_data,
    update_streamlit=True,
    key=f"canvas_{st.session_state.mode}_{st.session_state.scale}"
)

# Обработка изменений на холсте
if canvas_result.json_data is not None:
    new_objects = canvas_result.json_data.get("objects", [])
    
    new_base_points = []
    for obj in new_objects:
        if obj["type"] == "circle":
            # Центр точки с учетом originY
            center_x = obj["left"] + obj["radius"]
            if obj.get("originY") == "center":
                center_y = obj["top"]  # Уже центр
            else:
                center_y = obj["top"] + obj["radius"]
            
            # Обратное масштабирование координат и размера
            base_x = center_x / st.session_state.scale
            base_y = center_y / st.session_state.scale
            base_size = obj["radius"] / st.session_state.scale
            
            # Цвет без прозрачности
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