import streamlit as st
from config.styles import setup_step1_config
import numpy as np
import math

import matplotlib.pyplot as plt
import seaborn as sns




# --- RENDER: БОКОВАЯ ПАНЕЛЬ --------------------------------------

def render_result_sidebar():
    """Боковая панель для шага 2: разметка изображения точками"""
    st.markdown("""
    <h3 style='font-size: 18px; margin-bottom: 15px;'>
        Step 2: images marking
    </h3>
    """, unsafe_allow_html=True)

    # Вкладка "View the results"
    with st.expander("**View the results**", expanded=False):
        st.markdown("---")


        # Выбор режима
        view_container = st.container()
        with view_container:
            st.session_state.view = st.radio(
                "Choose view mode",
                ["Histograms", "Parameters"],
                label_visibility="collapsed"
            )
        




    # Настройка гистограмм
    if st.session_state.view == "Histograms":

        with st.expander("**Settings of histograms**", expanded=False):
            st.markdown("---")

            # Промежуток S
            all_areas = sum(st.session_state.data["areas"], [])
            max_area = max(all_areas) * 1.1
            max_area = int(math.ceil(max_area / 100.0) * 100)

            # 1) Считываем из session_state, если нет — инициализируем
            default_S_min = st.session_state.get("S_min", 0)
            default_S_max = st.session_state.get("S_max", max_area)

            # 2) Создаем слайдер, указывая начальные значения из session_state
            S_min, S_max = st.slider(
                "Range of areas",
                min_value=0,
                max_value=max_area,
                value=(default_S_min, default_S_max),
                step=100
            )

            # 3) Сохраняем обновлённые значения в session_state
            st.session_state.S_min = S_min
            st.session_state.S_max = S_max



            # Количество бинов
            new_bins = st.slider("Bins", 4.0, 100.0, st.session_state.bins, 2.0)
            if new_bins != st.session_state.bins:
                st.session_state.bins = new_bins
                st.rerun()
            



            st.markdown("---")

            st.session_state.histograms = st.radio(
                "Histograms mode",
                ["1 histogram", "2 histograms"]
            )
            

            if st.session_state.histograms == "1 histogram":
                image_names = ['General'] + st.session_state.data["image_names"]
                if "selected_histogram_image" not in st.session_state:
                    st.session_state.selected_histogram_image = image_names[0]

                st.session_state.selected_histogram_image = st.selectbox(
                    "Choose data",
                    options=image_names
                )


            elif st.session_state.histograms == "2 histograms":
                image_names = ['General'] + st.session_state.data["image_names"]
                if "selected_histogram_image_2_1" not in st.session_state:
                    st.session_state.selected_histogram_image_2_1 = image_names[0]
                if "selected_histogram_image_2_2" not in st.session_state:
                    st.session_state.selected_histogram_image_2_2 = image_names[1]

                st.session_state.selected_histogram_image_2_1 = st.selectbox(
                    "Choose data 1",
                    options=image_names
                )
                st.session_state.selected_histogram_image_2_2 = st.selectbox(
                    "Choose data 2",
                    options=image_names
                )



    elif st.session_state.view == "Parameters":

        with st.expander("**Settings of parameters**", expanded=False):
            st.markdown("---")

            # Инициализация параметров-флагов в session_state
            PARAMETER_OPTIONS = {
                "count": "Number of complete clusters",
                "sum_area": "Total area",
                "cut_area": "Cut-out area",  # если есть более точный контекст, можно уточнить
                "mean": "Mean area",
                "min": "Minimum area",
                "max": "Maximum area",
                "std": "Standard deviation",
                "cv": "Coefficient of variation"
            }

            if "selected_parameters" not in st.session_state:
                st.session_state.selected_parameters = {key: True for key in PARAMETER_OPTIONS}

            # Отображение чекбоксов
            for key, label in PARAMETER_OPTIONS.items():
                st.session_state.selected_parameters[key] = st.checkbox(
                    label,
                    value=st.session_state.selected_parameters.get(key, True),
                    key=f"checkbox_param_{key}"
                )







# --- RENDER: ОСНОВНОЕ ОКНО --------------------------------------

def render_result_page():
    """Основное окно для шага 2: разметка изображения точками"""
    setup_step1_config()

    if st.session_state.view == "Histograms":

            if st.session_state.histograms == "1 histogram":
                # Находим индекс выбранного изображения
                selected_image = st.session_state.selected_histogram_image

                if selected_image == 'General':
                    areas = sum(st.session_state.data["areas"], [])
                else:
                    image_names = st.session_state.data["image_names"]
                    selected_index = image_names.index(selected_image)
                    areas = st.session_state.data["areas"][selected_index]

                # Отрисовка гистограммы
                fig = plot_area_histogram(areas, st.session_state.bins, title=f"Histogram of cluster area for {selected_image}", label=selected_image, S_min=st.session_state.S_min, S_max=st.session_state.S_max)
                st.pyplot(fig)


            elif st.session_state.histograms == "2 histograms":
                # Находим индекс выбранного изображения
                selected_image_2_1 = st.session_state.selected_histogram_image_2_1
                selected_image_2_2 = st.session_state.selected_histogram_image_2_2

                if selected_image_2_1 == 'General':
                    areas_2_1 = sum(st.session_state.data["areas"], [])
                else:
                    image_names = st.session_state.data["image_names"]
                    selected_index_2_1 = image_names.index(selected_image_2_1)
                    areas_2_1 = st.session_state.data["areas"][selected_index_2_1]

                if selected_image_2_2 == 'General':
                    areas_2_2 = sum(st.session_state.data["areas"], [])
                else:
                    image_names = st.session_state.data["image_names"]
                    selected_index_2_2 = image_names.index(selected_image_2_2)
                    areas_2_2 = st.session_state.data["areas"][selected_index_2_2]

                # Отрисовка гистограммы
                fig = plot_area_histogram_2(areas_2_1, areas_2_2, st.session_state.bins, title=f"Histogram of cluster area for {selected_image_2_1} and {selected_image_2_2}", label = (selected_image_2_1, selected_image_2_2), S_min=st.session_state.S_min, S_max=st.session_state.S_max)
                st.pyplot(fig)




    elif st.session_state.view == "Parameters":
        import pandas as pd
        import numpy as np

        image_names = st.session_state.data["image_names"]
        image_areas = st.session_state.data["areas"]
        image_sizes = st.session_state.data["image_sizes"]
        bbox_sizes = st.session_state.data["bbox_sizes"]
        selected = st.session_state.selected_parameters

        table_rows = []

        # -------- Генеральные значения --------
        all_areas = np.concatenate(image_areas)
        total_clusters = len(all_areas)
        total_sum_area = all_areas.sum()
        total_mean = total_sum_area / total_clusters if total_clusters > 0 else 0
        total_std = all_areas.std()
        total_cv = total_std / total_mean if total_mean != 0 else None
        total_min = all_areas.min() if total_clusters > 0 else None
        total_max = all_areas.max() if total_clusters > 0 else None
        total_cut_area = sum(w * h for w, h in image_sizes) - total_sum_area

        general_row = {
            "Image": "General",
            "Size": "—",
            "Bbox size": "—"
        }

        if selected.get("count"):
            general_row["Number of complete clusters"] = total_clusters

        if selected.get("sum_area"):
            general_row["Total area"] = int(total_sum_area)

        if selected.get("cut_area"):
            general_row["Cut-out area"] = int(total_cut_area)

        if selected.get("mean"):
            general_row["Mean area"] = int(total_mean)

        if selected.get("min"):
            general_row["Minimum area"] = int(total_min)

        if selected.get("max"):
            general_row["Maximum area"] = int(total_max)

        if selected.get("std"):
            general_row["Standard deviation"] = int(total_std)

        if selected.get("cv"):
            general_row["Coefficient of variation"] = round(total_cv, 3)

        table_rows.append(general_row)

        # -------- По каждому изображению --------
        for name, areas, size, bbox in zip(image_names, image_areas, image_sizes, bbox_sizes):
            row = {
                "Image": name,
                "Size": (size[0], size[1]),
                "Bbox size": ((int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])))
            }
            np_areas = np.array(areas)
            width, height = size
            image_area_total = width * height
            sum_area = np_areas.sum()
            mean = np_areas.mean()

            if selected.get("count"):
                row["Number of complete clusters"] = len(np_areas)

            if selected.get("sum_area"):
                row["Total area"] = int(sum_area)

            if selected.get("cut_area"):
                cut = image_area_total - sum_area
                row["Cut-out area"] = int(cut)

            if selected.get("mean"):
                row["Mean area"] = int(mean)

            if selected.get("min"):
                row["Minimum area"] = int(np_areas.min())

            if selected.get("max"):
                row["Maximum area"] = int(np_areas.max())

            if selected.get("std"):
                std = np_areas.std()
                row["Standard deviation"] = int(std)

            if selected.get("cv"):
                row["Coefficient of variation"] = round(np_areas.std() / mean, 3) if mean != 0 else None

            table_rows.append(row)

        df = pd.DataFrame(table_rows)

        st.subheader("Parameters")
        st.dataframe(df, use_container_width=True)


        


def plot_area_histogram(areas, bins, title="", label="", bw_adjust=0.3, S_min=0, S_max=300000):
    """
    Рисует стилизованную гистограмму с KDE по списку площадей
    с возможностью ограничения по оси X. Фильтрует данные и
    обрезает KDE в пределах заданного диапазона.
    """

    fig = plt.figure(figsize=(8, 4))

    # 1. Фильтрация данных по выбранному диапазону
    data_in_range = [a for a in areas if S_min <= a <= S_max]

    # 2. Формируем массив «границ бинов»
    #    Исходя из глобального диапазона (как у тебя было),
    #    чтобы сохранить общую «ширину» бинов.
    all_areas = sum(st.session_state.data["areas"], [])
    bin_width = (max(all_areas) * 1.1) / bins
    bin_edges = np.arange(S_min, S_max + bin_width, bin_width)

    # 3. Отрисовываем гистограмму + KDE
    #    - clip=(S_min, S_max) обрезает KDE по границам
    #    - cut=0 не даёт KDE «вылезать» за крайние точки
    sns.histplot(
        data_in_range,
        bins=bin_edges,
        stat='density',
        kde=True,
        kde_kws={
            'bw_adjust': bw_adjust,
            'clip': (S_min, S_max),
            'cut': 0
        },
        label=label
    )

    plt.xlim(left=S_min, right=S_max)
    plt.legend()
    plt.title(title)
    plt.xlabel('Area')
    plt.ylabel('Density of probability')
    plt.grid(True)
    return fig


def plot_area_histogram_2(areas_1, areas_2, bins, title="", label=("", ""), bw_adjust=0.3, S_min=0, S_max=300000):
    """
    Рисует стилизованную гистограмму с KDE по списку площадей
    с возможностью ограничения по оси X. Фильтрует данные и
    обрезает KDE в пределах заданного диапазона.
    """

    fig = plt.figure(figsize=(8, 4))

    # 1. Фильтрация данных по выбранному диапазону
    data_1 = [a for a in areas_1 if S_min <= a <= S_max]
    data_2 = [a for a in areas_2 if S_min <= a <= S_max]

    # 2. Формируем массив «границ бинов»
    #    Исходя из глобального диапазона (как у тебя было),
    #    чтобы сохранить общую «ширину» бинов.
    all_areas = sum(st.session_state.data["areas"], [])
    bin_width = (max(all_areas) * 1.1) / bins
    bin_edges = np.arange(S_min, S_max + bin_width, bin_width)

    label_1, label_2 = label

    # 3. Отрисовываем гистограмму + KDE
    # Отрисовка первой гистограммы
    sns.histplot(
        data_1,
        bins=bin_edges,
        stat='density',
        kde=True,
        kde_kws={
            'bw_adjust': bw_adjust,
            'clip': (S_min, S_max),
            'cut': 0
        },
        label=label_1,
        color="blue",
        alpha=0.5
    )

    # Отрисовка второй гистограммы
    sns.histplot(
        data_2,
        bins=bin_edges,
        stat='density',
        kde=True,
        kde_kws={
            'bw_adjust': bw_adjust,
            'clip': (S_min, S_max),
            'cut': 0
        },
        label=label_2,
        color="orange",
        alpha=0.5
    )

    plt.xlim(left=S_min, right=S_max)
    plt.legend()
    plt.title(title)
    plt.xlabel('Area')
    plt.ylabel('Density of probability')
    plt.grid(True)
    return fig