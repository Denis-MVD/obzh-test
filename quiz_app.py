import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import os
import base64
from streamlit_autorefresh import st_autorefresh

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С ФОНОМ ---
def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return None

def set_png_as_page_bg(bin_file):
    bin_str = get_base64_of_bin_file(bin_file)
    if bin_str:
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        div[data-testid="stVerticalBlock"] > div:has(h1, h2, h3, h4, .stTextInput, .stSelectbox, .stButton, .stExpander, p, span) {{
            background-color: rgba(61, 68, 50, 0.85) !important;
            padding: 25px; 
            border-radius: 15px; 
            border-left: 10px solid #2f3526 !important;
            box-shadow: 10px 10px 25px rgba(0,0,0,0.6);
            margin-bottom: 15px;
        }}

        div[data-testid="stVerticalBlock"] > div:not(:has(*)) {{
            display: none !important;
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="НВП: Контроль", layout="centered", page_icon="🎖️")
set_png_as_page_bg('background.png')

# --- 2. КОНСТАНТЫ ---
TEACHER_PIN = "1234"
RESULTS_FILE = "detailed_results.csv"
TEST_DURATION_MIN = 15 

# --- 3. БАЗА ВОПРОСОВ ПО ТЕМАМ ---
DATABASE = {
    "10 класс": {
        "Тема 1: Основы ГО": [
            ("Что сделать при сигнале «Внимание всем!»?", ["Бежать на улицу", "Включить ТВ или радио", "Спрятаться в подвале"], "Включить ТВ или радио"),
            ("Главный фактор землетрясения?", ["Цунами", "Разрушение зданий", "Гроза"], "Разрушение зданий"),
        ],
        "Тема 2: Природные ЧС": [
            ("Что такое сель?", ["Лавина", "Грязекаменный поток", "Ветер"], "Грязекаменный поток"),
            ("Землетрясение на улице. Где находиться?", ["У высокого здания", "На открытой площадке", "В машине"], "На открытой площадке"),
        ],
        "Тема 3: Пожарная безопасность": [
            ("Пожар в школе. Первое действие?", ["Урок продолжать", "Эвакуация и вызов 101", "Окна открыть"], "Эвакуация и вызов 101"),
            ("Выход из лесного пожара:", ["По ветру", "Против ветра", "На месте"], "Против ветра, перпендикулярно кромке"),
        ]
    },
    "11 класс": {
        "Тема 1: Техногенные аварии": [
            ("Авария на АЭС. Первое действие?", ["Балкон", "Йодная профилактика", "Окна открыть"], "Йодная профилактика и герметизация"),
            ("Признак радиации:", ["Запах", "Звук", "Нет (только приборами)"], "Нет (только приборами)"),
        ],
        "Тема 2: Терроризм и защита": [
            ("Сообщение о терроризме:", ["Игнор", "Полиция, не трогать предметы", "Сам осмотрю"], "Полиция, не трогать предметы"),
            ("Коллективные средства защиты:", ["Противогаз", "Убежища и укрытия", "Аптечка"], "Убежища и укрытия"),
        ]
    }
}

# --- 4. ФУНКЦИИ ---
def save_result_to_file(data):
    file_exists = os.path.isfile(RESULTS_FILE)
    df = pd.DataFrame([data])
    df.to_csv(RESULTS_FILE, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')

def get_grade(score, total):
    perc = (score / total) * 100
    if perc >= 90: return "5 (Отлично)"
    elif perc >= 75: return "4 (Хорошо)"
    elif perc >= 50: return "3 (Удовл.)"
    else: return "2 (Неуд.)"

# --- 5. ЛОГИКА СОСТОЯНИЙ ---
if 'test_state' not in st.session_state: st.session_state.test_state = "login"
if 'results_saved' not in st.session_state: st.session_state.results_saved = False
if 'selected_class' not in st.session_state: st.session_state.selected_class = None

# --- 6. ЭКРАН 1: ВХОД ---
if st.session_state.test_state == "login":
    st.markdown("<h4 style='text-align: center; color: #dcdcdc; margin: 0;'>Преподаватель по начальной военной подготовке</h4>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #ffffff; margin: 0;'>Семенков Денис Алексеевич</h3>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white; text-transform: uppercase;'>🎖️ КОНТРОЛЬ ЗНАНИЙ ПО НВП</h2>", unsafe_allow_html=True)
    
    name = st.text_input("Фамилия и Имя ученика:")
    
    # Выбор класса
    col1, col2 = st.columns(2)
    if col1.button("10 КЛАСС 📘", use_container_width=True):
        st.session_state.selected_class = "10 класс"
    if col2.button("11 КЛАСС 📕", use_container_width=True):
        st.session_state.selected_class = "11 класс"

    # Если класс выбран, показываем темы
    if st.session_state.selected_class:
        st.markdown(f"<h5 style='color: gold;'>Выбран: {st.session_state.selected_class}. Выберите тему теста:</h5>", unsafe_allow_html=True)
        
        themes = DATABASE[st.session_state.selected_class]
        for theme_name in themes.keys():
            if st.button(theme_name, use_container_width=True):
                if name:
                    st.session_state.name = name
                    st.session_state.u_class = st.session_state.selected_class
                    st.session_state.theme = theme_name
                    st.session_state.start_time = datetime.now()
                    st.session_state.results_saved = False
                    
                    # Загрузка вопросов темы
                    raw_q = themes[theme_name]
                    shuffled = []
                    for q_text, opts, corr in random.sample(raw_q, len(raw_q)):
                        sh_opts = random.sample(opts, len(opts))
                        shuffled.append((q_text, sh_opts, corr))
                    
                    st.session_state.questions = shuffled
                    st.session_state.test_state = "testing"
                    st.rerun()
                else:
                    st.error("Введите имя перед началом!")

    with st.expander("📊 КАБИНЕТ ПРЕПОДАВАТЕЛЯ"):
        pin = st.text_input("PIN:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                st.dataframe(pd.read_csv(RESULTS_FILE), use_container_width=True)

# --- 7. ЭКРАН 2: ТЕСТИРОВАНИЕ ---
elif st.session_state.test_state == "testing":
    st_autorefresh(interval=5000, key="timer_refresh")
    elapsed = datetime.now() - st.session_state.start_time
    rem = timedelta(minutes=TEST_DURATION_MIN) - elapsed
    
    if rem.total_seconds() <= 0:
        st.session_state.test_state = "finishing"
        st.rerun()

    st.markdown(f"### 👤 {st.session_state.name} | {st.session_state.theme}")
    
    user_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        st.markdown(f"**{i+1}. {q}**")
        ans = st.radio(f"Выбор {i}", opts, key=f"q_{i}", index=None, label_visibility="collapsed")
        user_ans.append(ans)

    if st.button("ЗАКОНЧИТЬ ТЕСТ ✅"):
        if None in user_ans:
            st.warning("Ответьте на все вопросы!")
        else:
            st.session_state.user_ans = user_ans
            st.session_state.test_state = "finishing"
            st.rerun()

# --- 8. ЭКРАН 3: ИТОГИ ---
elif st.session_state.test_state == "finishing":
    score = sum(1 for i, (q, opts, corr) in enumerate(st.session_state.questions) if st.session_state.user_ans[i] == corr)
    total = len(st.session_state.questions)
    grade = get_grade(score, total)
    
    if not st.session_state.results_saved:
        save_result_to_file({
            "Дата": datetime.now().strftime("%d.%m %H:%M"), 
            "ФИО": st.session_state.name, 
            "Класс": st.session_state.u_class,
            "Тема": st.session_state.theme,
            "Баллы": f"{score}/{total}", 
            "Оценка": grade
        })
        st.session_state.results_saved = True

    st.markdown(f"<h1 style='text-align: center; color: white;'>Результат: {score} из {total}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; color: gold;'>Оценка: {grade}</h2>", unsafe_allow_html=True)
    
    if st.button("ВЕРНУТЬСЯ В МЕНЮ"):
        st.session_state.test_state = "login"
        st.session_state.selected_class = None
        st.rerun()
