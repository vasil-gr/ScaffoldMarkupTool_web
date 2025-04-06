import streamlit as st
from config.styles import setup_step1_config

import zipfile
from PIL import Image
import json
import os
import math


# --- RENDER: БОКОВАЯ ПАНЕЛЬ --------------------------------------

def render_upload_sidebar():
    """Боковая панель для шага 1: загрузка данных (изображения или архива)"""
    st.markdown("""
    <h3 style='font-size: 18px; margin-bottom: 15px;'>
        Step 1: Uploading data
    </h3>
    """, unsafe_allow_html=True)

    # Загрузчик файлов
    uploaded_file = st.file_uploader(
        "**Choose an image or project archive**",
        type=["png", "jpg", "jpeg", "bmp", "gif", "tiff", "zip"],
        key="file_uploader_step1"
    )

    # Если загружен файл
    if uploaded_file is not None:

        # ZIP-архив:
        if uploaded_file.type == "application/zip" or uploaded_file.name.endswith('.zip'):
            try:
                if validate_zip_contents(uploaded_file): # валидация содержимого
                    # разорхивация изображения
                    img, img_name = extract_image_from_zip(uploaded_file)
                    st.session_state.original_img = img
                    st.session_state.image_name = img_name

                    # разорхивация json-файла (и загрузка точек из него)
                    points = load_points_from_json(uploaded_file)
                    if points:
                        st.session_state.base_points = points
                else:
                    st.error("Zip archive must contain exactly one PNG image and one JSON file") # ошибка содержимого архива (напечатается)
            except Exception as e:
                st.error(f"Error processing zip file: {str(e)}") # другие ошибки (напечатаются)

        # Простое изображение:
        else:
            try:
                img = Image.open(uploaded_file).convert("RGB")
                st.session_state.original_img = img
                st.session_state.image_name = uploaded_file.name
                st.session_state.base_points = None
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
    
    # Исходя из размеров изображения, мы можем подобрать начальный масштаб и пределы слайдера
    if st.session_state.original_img is not None:
        initial_scale, min_scale, max_scale = calculate_safe_scale(st.session_state.original_img.size[0])
        st.session_state.initial_scale = initial_scale # понадобится для сброса масштаба
        st.session_state.scale = initial_scale
        st.session_state.min_scale = min_scale
        st.session_state.max_scale = max_scale
                

# --- RENDER: ОСНОВНОЕ ОКНО --------------------------------------

def render_upload_page():
    """Основное окно для шага 1: загрузка данных (изображения или архива)"""
    setup_step1_config()

    st.write("### Scaffold Markup Tool")
    st.write("Here you can read how to work in the program: [Help](#)")  # ! тут будет ссылка
    
    if st.session_state.get('original_img'):
        if st.session_state.base_points is not None:
            st.success(f"✅ Image and {len(st.session_state.base_points)} points from archive successfully uploaded!")
        else:
            st.success("✅ Image successfully uploaded!")
        
        st.image(st.session_state.original_img, caption="Uploaded Image")
        st.write("Uploaded dots:", st.session_state.base_points)
        st.write(st.session_state.step2_initial_render)
    
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

        # Пример
        with st.expander("Show format examples"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Single Image Example**")
                st.image("image_example.jpg", width=150)
            with col2:
                st.write("**Project ZIP Contents**")
                st.code("""
        my_project.zip
        ├── image.png      # Unmarked image
        └── data.json      # Point coordinates & metadata
                """)




# --- UTILS: РАБОТА С ZIP-АРХИВАМИ -------------------------------------

def validate_zip_contents(zip_file):
    """Проверка, что ZIP-архив содержит ровно один PNG и один файл JSON""" 
    with zipfile.ZipFile(zip_file) as z:
        file_list = z.namelist()
        png_files = [f for f in file_list if f.lower().endswith('.png')]
        json_files = [f for f in file_list if f.lower().endswith('.json')]
        return len(png_files) == 1 and len(json_files) == 1


def extract_image_from_zip(zip_file):
    """Извлечение изображения из ZIP-архива, как PIL.Image"""
    with zipfile.ZipFile(zip_file) as z:
        file_list = z.namelist()
        png_file = next(f for f in file_list if f.lower().endswith('.png'))
        with z.open(png_file) as f:
            return Image.open(f).convert("RGB"), os.path.basename(png_file)


def load_points_from_json(zip_file):
    """Извлечение JSON-файла из ZIP-файла и валидация данных о точках""" 
    with zipfile.ZipFile(zip_file) as z:
        # Находим JSON-файл в архиве
        json_files = [f for f in z.namelist() if f.lower().endswith('.json')]
        if not json_files:
            return None
        
        # Читаем JSON-файл
        json_file = json_files[0]
        with z.open(json_file) as f:
            try:
                json_data = json.load(f)
            except json.JSONDecodeError:
                return None
        
        # Проверяем обязательные поля
        if not all(key in json_data for key in ['image_name', 'points']):
            return None
        
        # Валидация точек
        valid_points = []
        for point in json_data['points']:
            if not all(k in point for k in ['x', 'y', 'weight', 'size', 'color']):
                continue
            try:
                valid_points.append({
                    'x': float(point['x']),
                    'y': float(point['y']),
                    'weight': float(point['weight']),
                    'size': float(point['size']),
                    'color': point['color']
                })
            except (ValueError, TypeError):
                continue
        
        return valid_points # возвращает координаты точек в стиле st.session_state.base_points



# --- UTILS: РАСЧЁТ МАСШТАБОВ ОТОБРАЖЕНИЯ ------------------------------

def calculate_safe_scale(original_width):
    """Расчёт оптимальных значений масштаба: начального, минимального и максимального"""
    # Стартовый масштаб
    if original_width <= st.session_state.display_width:
        initial_scale = 1.0
    else:
        scale_factor = st.session_state.display_width / original_width
        initial_scale = math.floor(scale_factor / st.session_state.scale_step) * st.session_state.scale_step
        initial_scale = round(initial_scale, 2)
    
    # Минимальный масштаб
    min_scale_raw = st.session_state.min_width / original_width
    min_scale = math.ceil(min_scale_raw / st.session_state.scale_step) * st.session_state.scale_step
    min_scale = max(0.1, round(min_scale, 2))
    
    # Максимальный масштаб (округляем вверх, если не превышает MAX_WIDTH)
    max_scale_raw = st.session_state.max_width / original_width
    max_scale_rounded_up = math.ceil(max_scale_raw / st.session_state.scale_step) * st.session_state.scale_step

    if (max_scale_rounded_up * original_width) <= st.session_state.max_width:
        max_scale = max_scale_rounded_up
    else:
        max_scale = math.floor(max_scale_raw / st.session_state.scale_step) * st.session_state.scale_step
    
    max_scale = min(3.0, round(max_scale, 2))
    
    # Гарантируем, что initial_scale находится в границах
    initial_scale = max(min(initial_scale, max_scale), min_scale)
    return initial_scale, min_scale, max_scale
