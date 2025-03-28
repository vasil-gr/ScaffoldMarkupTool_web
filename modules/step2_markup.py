import streamlit as st
from config.styles import setup_step2_config, setup_step2_config_frame
import math

from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw
import io
import os
import json
from datetime import datetime
import zipfile


# --- RENDER: sidebar --------------------------------------

def render_markup_sidebar():
    st.markdown("""
    <h3 style='font-size: 18px; margin-bottom: 15px;'>
        Step 2: images marking
    </h3>
    """, unsafe_allow_html=True)
    
    # Вкладка "Tools"
    with st.expander("**Tools**", expanded=False):

        st.markdown("---")
        
        # Подраздел 1: выбор режима
        edit_container = st.container()
        with edit_container:
            st.markdown("**▸ Mode**")

            col1, col2 = st.columns([6, 3])
            with col1:
                # Выбор режима (рисовать/редактировать)
                mode_radio = st.radio(
                    "Mode",
                    ("Adding dots", "Editing dots"),
                    index=0 if st.session_state.mode == "draw" else 1, 
                    label_visibility="collapsed"
                )
                new_mode = "draw" if mode_radio == "Adding dots" else "edit"
                if new_mode != st.session_state.mode:
                    st.session_state.mode = new_mode
                    st.session_state.canvas_data = generate_canvas_data()

            with col2:
                # Удаление всех точек
                if st.button("Clear", disabled=not st.session_state.base_points):
                    st.session_state.base_points.clear()
                    st.session_state.canvas_data = {"version": "4.6.0", "objects": []}
                    st.session_state.redraw_id += 1 # так как эта переменная финурирует в ключе холста, то ее изменение перезагрузит холст

        # Разделитель
        st.markdown("---")

        # Подраздел 2: Zoom
        zoom_container = st.container()
        with zoom_container:
            st.markdown("**▸ Zoom**")
            col5, col6 = st.columns([6, 3])
            
            with col5:
                # Слайдер масштаба
                new_scale = st.slider("Zoom", st.session_state.min_scale, st.session_state.max_scale, st.session_state.scale, st.session_state.scale_step, label_visibility="collapsed")
                if new_scale != st.session_state.scale:
                    st.session_state.scale = new_scale
                    st.session_state.canvas_data = generate_canvas_data()

            with col6:
                # Сброс масштаба
                if st.button("Reset", key="zoom_reset", help="Zoom reset"):
                    new_scale = st.session_state.initial_scale
                    if new_scale != st.session_state.scale:
                        st.session_state.scale = new_scale
                        st.session_state.canvas_data = generate_canvas_data()


        # Разделитель
        st.markdown("---")

        # Подраздел 3: настройка точек
        size_container = st.container()
        with size_container:
            st.markdown("**▸ Dot settings**")
            col3, col4 = st.columns([6, 3])

            # Настройки для новых точек (не влияют на существующие)
            with col3:
                # Слайдер размера точек
                st.session_state.current_point_size = st.slider("Size", min_value=1, max_value=20, value=st.session_state.current_point_size, key="size_slider")
            with col4:
                # Палитра выбора цвета точек
                st.session_state.current_point_color = st.color_picker("Color", st.session_state.current_point_color, key="color_picker")


            
    # Вкладка "Save"
    with st.expander("**Save**", expanded=False):

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
            if st.button("Prepare", key="load_button"):
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
                label="Download",
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



# --- RENDER: основное окно --------------------------------------

def render_markup_page():

    # Конфигурация страницы (втч горизонатальная полоса прокрутки)
    setup_step2_config()

    # Интерфейс

    # Масштабирование изображения
    scaled_width = int(st.session_state.original_img.size[0] * st.session_state.scale)
    scaled_height = int(st.session_state.original_img.size[1] * st.session_state.scale)

    # динамически адаптируем размер холста под размер изображения (в зависимости от его масштаба)
    setup_step2_config_frame(scaled_width)

    # Загрузка точек на холст (для случая открытия проекта)
    if st.session_state.step2_initial_render:
        if st.session_state.base_points is not None:
            st.session_state.canvas_data = generate_canvas_data()
        else:
            st.session_state.canvas_data = {"version": "4.6.0", "objects": []}
        st.session_state.step2_initial_render = False
    # Холст
    canvas_result = st_canvas(
        fill_color=st.session_state.current_point_color + "B3",  # Добавляем прозрачность
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
                # Определяем центр точки с учетом originY
                center_x = obj["left"] + obj["radius"]
                if obj.get("originY") == "center":
                    center_y = obj["top"]  # Уже центр
                else:
                    center_y = obj["top"] + obj["radius"]
                
                # Обратное масштабирование координат и размера
                base_x = center_x / st.session_state.scale
                base_y = center_y / st.session_state.scale
                base_size = obj["radius"] / st.session_state.scale
                
                # Получаем цвет без прозрачности
                color = obj["fill"][:7] if obj["fill"].startswith('#') else "#FF0000"  # fallback
                
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





# --- UTILS: Функции для сохранения --------------------------------------

# Функция для добавление точек на изображение
def add_dots_to_image(new_image):
    """Наносит точки на изображение"""
    if st.session_state.base_points:  # Рисуем точки только если они есть
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
    
    # Создаем байтовый поток
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
    transparent_img = Image.new('RGBA', (st.session_state.original_img.size[0], st.session_state.original_img.size[1]), (0, 0, 0, 0)) # прозрачный фон (режим 'RGBA')
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
            "value_per_pixel": None  # Можно заменить на реальное значение
        },
        "creation_date": datetime.now().strftime("%Y-%m-%d"),
        "author": "user",  # Можно заменить на реальное значение
        "notes": None  # Можно добавить поле для заметок
    }
    
    # Конвертируем в JSON строку
    json_str = json.dumps(points_data, indent=4)
    
    # Создаем байтовый поток
    json_bytes = io.BytesIO(json_str.encode('utf-8'))
    json_bytes.seek(0)
    return json_bytes

    
# Функция для сохранения проекта (архив исходного изображения и json-файла с точками)
def save_project():
    """Создает ZIP-архив с исходным изображением и JSON-файлом точек"""
    # Создаем байтовый поток для ZIP-архива
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # 1. Добавляем исходное изображение
        img_byte_arr = io.BytesIO()
        st.session_state.original_img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        zipf.writestr(f"{st.session_state.image_name}.png", img_byte_arr.getvalue())
        
        # 2. Добавляем JSON с точками
        json_data = save_points()  # Используем существующую функцию
        zipf.writestr(f"{st.session_state.image_name}_points.json", json_data.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer




# --- UTILS: данные CANVAS --------------------------

def get_scaled_points():
    """Возвращает масштабированные точки с их параметрами"""
    return [
        {
            'x': point['x'] * st.session_state.scale,
            'y': point['y'] * st.session_state.scale,
            'size': point['size'] * st.session_state.scale,
            'color': f"{point['color']}B3"  # Добавляем фиксированную прозрачность 0.7 (B3 в hex)
        }
        for point in st.session_state.base_points
    ]

# Генерация данных для холста
def generate_canvas_data():
    if st.session_state.base_points is not None:
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
