import streamlit as st

def init_session_state_markup_app():
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

        # Инициализация download_option_3 - вариант скачивания на третьем шаге
        "download_option_3": None,
        "download_option_ind_3": None,
        "data_ready_3": False,
        "download_data_3": None,

        # Инициализация флага первого рендера на шаге 2
        "step2_initial_render": True,
        "step2_img_render": True,
        # счётчик перерисовок (при нажатии кнопки "Clear"), нужен чтобы обновлять canvas
        "redraw_id": 0,
        # Инициация перехода на шаг 3 для прорисовки изобаржения
        "step3_img_render": True,

        # Инициализация состояний переключателей на шаге 3
        "show_img": True,
        "show_dots": True,
        "show_clasters": True,
        "show_filling": False,

        "current_claster_color": "#0000FF",
        "current_filling_color": "#FFB300",

        "last_handled_coords": None,

        "initial_weight": 0.0,
        "mode_3": "draw",
        "plas_weight": -30.0,
        "weight": -50.0,
        "min_weight": -200.0,
        "max_weight": 200.0,
        "weight_step": 10.0,

        "box_x_min": 0.0,
        "box_y_min": 0.0,
        "box_w": 2560.0, # нужно переопределить на пользовательские
        "box_h": 1920.0,


        # Help section
        "section": "About app",

    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value



def init_session_state_analysis_app():
    """Инициализация переменных"""

    defaults = {
        "step_an": 1, # режимы (2)
        "sidebar_state": "expanded",
        "data": {                        # валидные данные из файлов
                "image_names": [],
                "image_sizes": [],
                "areas": []
                },
        "data_broken": [],            # невалидные данные из файлов
        "view": "View histograms",
        "histograms": "General histogram",
        "bins": 30.0,

    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value




def clear_session_state(app):

    markup_keys = [
        "sidebar_state",
        "original_img",
        "image_name",
        "step",
        "base_points",
        "canvas_data",
        "mode",
        "current_point_size",
        "current_point_color",

        "initial_scale",
        "scale",
        "min_scale",
        "max_scale",

        # Параметры безопасного масштаба
        "display_width",
        "max_width",
        "min_width",
        "scale_step",

        # Инициализация download_option - вариант скачивания на втором шаге
        "download_option",
        "download_option_ind",
        "data_ready",
        "download_data",

        # Инициализация download_option_3 - вариант скачивания на третьем шаге
        "download_option_3",
        "download_option_ind_3",
        "data_ready_3",
        "download_data_3",

        # Инициализация флага первого рендера на шаге 2
        "step2_initial_render",
        "step2_img_render",
        # счётчик перерисовок (при нажатии кнопки "Clear"), нужен чтобы обновлять canvas
        "redraw_id",
        # Инициация перехода на шаг 3 для прорисовки изобаржения
        "step3_img_render",

        # Инициализация состояний переключателей на шаге 3
        "show_img",
        "show_dots",
        "show_clasters",
        "show_filling",

        "current_claster_color",
        "current_filling_color",

        "last_handled_coords",

        "initial_weight",
        "mode_3",
        "plas_weight",
        "weight",
        "min_weight",
        "max_weight",
        "weight_step",

        "box_x_min",
        "box_y_min",
        "box_w",
        "box_h",

        # Help section
        "section"
    ]


    analysis_keys = [
        "step_an",
        "sidebar_state",
        "data",
        "data_broken",
        "view",
        "histograms",
        "bins",
    ]

    if app == 'analysis':
        for key in analysis_keys:
            if key in st.session_state:
                del st.session_state[key]
    elif app == 'markup':
        for key in markup_keys:
            if key in st.session_state:
                del st.session_state[key]
