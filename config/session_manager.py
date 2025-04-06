import streamlit as st

def init_session_state():
    """Инициализация переменных"""

    # Конфигурация
    INITIAL_POINT_SIZE = 10
    INITIAL_COLOR = "#FF0000"

    DISPLAY_WIDTH = 1500  # оптимальная ширина для начального отображения
    MAX_WIDTH = 2500 # максимальная ширина при увеличении
    MIN_WIDTH = 300 # минимальная ширина при уменьшении
    STEP = 0.05 # шаг изменения масштаба

    defaults = {
        "sidebar_state": "expanded",
        "original_img": None,
        "image_name": None,
        "step": 1, # режимы (3)
        "base_points": None, # {'x', 'y', 'weight', 'size', 'color'}
        "canvas_data": None,
        "mode": "draw",
        "current_point_size": INITIAL_POINT_SIZE,
        "current_point_color": INITIAL_COLOR,

        "initial_scale": 1.0,
        "scale": 1.0,
        "min_scale": 0.5,
        "max_scale": 1.5,

        # Параметры безопасного масштаба
        "display_width": DISPLAY_WIDTH,
        "max_width": MAX_WIDTH,
        "min_width": MIN_WIDTH,
        "scale_step": STEP,

        # Инициализация download_option - вариант скачивания на втором шаге
        "download_option": None,
        "download_option_ind": None,
        "data_ready": False,
        "download_data": None,

        # Инициализация флага первого рендера на шаге 2
        "step2_initial_render": True,
        # счётчик перерисовок (при нажатии кнопки "Clear"), нужен чтобы обновлять canvas
        "redraw_id": 0,
        # Инициация перехода на шаг 3 для прорисовки изобаржения
        "step3_img_render": True,

        # Инициализация состояний переключателей на шаге 3
        "show_img": True,
        "show_dots": True,
        "show_clasters": False,
        "show_filling": False,


    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

