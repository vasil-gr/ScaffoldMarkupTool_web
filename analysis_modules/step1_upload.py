import streamlit as st
from config.styles import setup_step1_config

import json
import os
import pandas as pd


# --- RENDER: БОКОВАЯ ПАНЕЛЬ --------------------------------------

import os
import json

def render_upload_sidebar():
    """Боковая панель для шага 1: загрузка данных (изображения или архива)"""
    st.markdown("""
    <h3 style='font-size: 18px; margin-bottom: 15px;'>
        Step 1: Uploading data
    </h3>
    """, unsafe_allow_html=True)

    # Загрузчик файлов
    uploaded_files = st.file_uploader(
        "**Choose JSON**",
        type=["json"],
        key="file_uploader_step1",
        accept_multiple_files=True
    )

    # Временные хранилища
    current_data = {
        "image_names": [],
        "image_sizes": [],
        "bbox_sizes": [],
        "areas": []
    }
    current_broken = []

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                content = uploaded_file.read()
                json_data = json.loads(content)

                valid = True

                # Проверка на обязательные ключи
                if "image_name" not in json_data or "image_size" not in json_data or "areas" not in json_data:
                    valid = False
                elif not isinstance(json_data["areas"], list) or len(json_data["areas"]) == 0:
                    valid = False
                elif not all(isinstance(a, (int, float)) for a in json_data["areas"]):
                    valid = False
                elif "width" not in json_data["image_size"] or "height" not in json_data["image_size"]:
                    valid = False
                elif "bbox_size" not in json_data or \
                    "x_min" not in json_data["bbox_size"] or "y_min" not in json_data["bbox_size"]:
                    valid = False

                if not valid:
                    raise ValueError("Invalid structure")

                # Имя изображения без расширения
                base_name = os.path.splitext(json_data.get("image_name", uploaded_file.name))[0]

                # Размер изображения
                image_size = [
                    json_data["image_size"]["width"],
                    json_data["image_size"]["height"]
                ]

                # Площади кластеров
                areas = json_data["areas"]

                # BBox
                x_min = json_data["bbox_size"]["x_min"]
                y_min = json_data["bbox_size"]["y_min"]

                if "w" in json_data["bbox_size"] and "h" in json_data["bbox_size"]:
                    x_max = x_min + json_data["bbox_size"]["w"]
                    y_max = y_min + json_data["bbox_size"]["h"]
                elif "x_max" in json_data["bbox_size"] and "y_max" in json_data["bbox_size"]:
                    x_max = json_data["bbox_size"]["x_max"]
                    y_max = json_data["bbox_size"]["y_max"]
                else:
                    raise ValueError("bbox_size format unsupported")

                bbox_size = [x_min, y_min, x_max, y_max]

                # Сравнение со всеми похожими именами
                existing_names = current_data["image_names"]
                similar_indexes = [
                    i for i, name in enumerate(existing_names)
                    if name == base_name or name.startswith(f"{base_name} (")
                ]

                is_duplicate = any(
                    current_data["image_sizes"][i] == image_size and
                    current_data["bbox_sizes"][i] == bbox_size
                    for i in similar_indexes
                )

                if is_duplicate:
                    # Это точный дубликат
                    if base_name not in current_broken:
                        current_broken.append(base_name)
                else:
                    # Нужно создать уникальное имя
                    image_name = base_name

                    current_data["image_names"].append(image_name)
                    current_data["image_sizes"].append(image_size)
                    current_data["bbox_sizes"].append(bbox_size)
                    current_data["areas"].append(areas)

            except Exception:
                image_name = os.path.splitext(uploaded_file.name)[0]
                if image_name not in current_broken:
                    current_broken.append(image_name)

    # Обновляем session_state
    st.session_state.data = current_data
    st.session_state.data_broken = current_broken



# --- RENDER: ОСНОВНОЕ ОКНО --------------------------------------

def render_upload_page():
    """Основное окно для шага 1: загрузка данных (изображения или архива)"""
    setup_step1_config()

    st.write("### Scaffold Markup Tool")
    st.write("Here you can read how to work in the program: [Help](#)")  # ! тут будет ссылка
    

    # Вывод успешной загрузки
    if st.session_state.data["image_names"]:
        st.success(f"✅ Successfully uploaded files: {len(st.session_state.data['image_names'])}")

        # Подготовка таблицы
        table_data = []
        for name, size, bbox, areas in zip(
            st.session_state.data["image_names"],
            st.session_state.data["image_sizes"],
            st.session_state.data["bbox_sizes"],
            st.session_state.data["areas"]
        ):
            size_str = f"{size[0]}×{size[1]}"
            bbox_str = f"({bbox[0]:.0f}, {bbox[1]:.0f}) → ({bbox[2]:.0f}, {bbox[3]:.0f})"
            cluster_count = len(areas)

            table_data.append({
                "Image": name,
                "Size": size_str,
                "Bbox size": bbox_str,
                "Number of complete clusters": cluster_count
            })

        df = pd.DataFrame(table_data)
        st.table(df)

    # Вывод ошибок
    if st.session_state.data_broken:
        st.warning(f"⚠️ Problem files: {len(st.session_state.data_broken)}")
        with st.expander("Show problem files"):
            for name in st.session_state.data_broken:
                st.markdown(f"- {name}")
    else:
        if not st.session_state.data["image_names"]:
            st.info("Download JSON-files to start.")