import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import os
import base64
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С ФОНОМ И ФОТО ---
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
        
        div[data-testid="stVerticalBlock"] > div {{
            background-color: rgba(61, 68, 50, 0.85) !important;
            padding: 25px; border-radius: 15px; 
            border-left: 10px solid #2f3526 !important;
            box-shadow: 10px 10px 25px rgba(0,0,0,0.6);
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)

# --- НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="НВП: Обучение и Контроль", layout="centered", page_icon="🎖️")
set_png_as_page_bg('background.png')

# --- КОНСТАНТЫ ---
TEACHER_PIN = "1234"
RESULTS_FILE = "detailed_results.csv"
TEST_DURATION_MIN = 15 
IMG_DIR = "фото" # Убедитесь, что папка называется так

# --- ЛОГИКА СОСТОЯНИЙ ---
if 'test_state' not in st.session_state: st.session_state.test_state = "login"
if 'results_saved' not in st.session_state: st.session_state.results_saved = False

# --- СТИЛИ ---
st.markdown("""
    <style>
    h1, h2, h3, h4, p, span, li { color: #ffffff !important; font-family: 'Segoe UI', sans-serif; font-weight: bold !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.9); }
    .stButton>button { background-color: #2f3526 !important; color: white !important; border: 2px solid #ffffff !important; width: 100%; height: 50px; font-size: 18px; }
    .lesson-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; border: 1px solid white; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- ВОПРОСЫ (сокращено для примера, используйте свои списки) ---
questions_10 = [
    ("Что изображено на учебном коллаже?", ["Сель, пожар, землетрясение", "Только наводнение", "Гроза", "Авария"], "Сель, пожар, землетрясение"),
    ("Безопасное место в здании по инфографике?", ["У окна", "Проем капитальных стен", "Лифт", "Балкон"], "Проем капитальных стен")
]
# Добавьте остальные свои вопросы сюда...

# --- ЭКРАН 1: ВХОД ---
if st.session_state.test_state == "login":
    st.markdown("<h1 style='text-align: center;'>🎖️ НВП: ГРАЖДАНСКАЯ ОБОРОНА</h1>", unsafe_allow_html=True)
    name = st.text_input("Введите Фамилию и Имя:")
    u_class = st.selectbox("Ваш класс:", ["10 класс", "11 класс"])
    
    if st.button("ПЕРЕЙТИ К ИЗУЧЕНИЮ МАТЕРИАЛА 📖"):
        if name:
            st.session_state.name = name
            st.session_state.u_class = u_class
            st.session_state.test_state = "lesson"
            st.rerun()
        else:
            st.error("Введите имя!")

# --- ЭКРАН 2: УРОК (НОВОЕ) ---
elif st.session_state.test_state == "lesson":
    st.markdown(f"# 📖 Учебный материал: {st.session_state.u_class}")
    
    # Блок 1: Виды ЧС
    with st.container():
        st.markdown("### 1. Основные природные угрозы")
        col_path = os.path.join(IMG_DIR, "collage.jpg")
        if os.path.exists(col_path):
            st.image(col_path, caption="Виды природных ЧС: Сель, Землетрясение, Пожар", use_container_width=True)
        else:
            st.warning("Файл 'collage.jpg' не найден в папке 'фото'")
        st.write("Запомните визуальные признаки каждой ситуации для быстрого реагирования.")

    # Блок 2: Действия при землетрясении
    with st.container():
        st.markdown("### 2. Алгоритм выживания в здании")
        info_path = os.path.join(IMG_DIR, "infografika.jpg")
        if os.path.exists(info_path):
            st.image(info_path, caption="Инструкция: Безопасное положение в проеме", use_container_width=True)
        else:
            st.warning("Файл 'infografika.jpg' не найден")
        st.markdown("""
        **Ключевые правила:**
        * Не поддавайтесь панике.
        * Используйте капитальные стены.
        * Защищайте голову руками.
        """)

    if st.button("Я ИЗУЧИЛ. НАЧАТЬ ТЕСТ! ✍️"):
        st.session_state.start_time = datetime.now()
        raw_q = questions_10 if st.session_state.u_class == "10 класс" else questions_11 # Убедитесь, что questions_11 определен
        st.session_state.questions = random.sample(raw_q, len(raw_q))
        st.session_state.test_state = "testing"
        st.rerun()

# --- ЭКРАН 3: ТЕСТИРОВАНИЕ ---
elif st.session_state.test_state == "testing":
    st_autorefresh(interval=5000, key="timer_refresh")
    elapsed = datetime.now() - st.session_state.start_time
    rem = timedelta(minutes=TEST_DURATION_MIN) - elapsed
    
    if rem.total_seconds() <= 0:
        st.session_state.test_state = "finishing"
        st.rerun()

    c1, c2 = st.columns([2, 1])
    c1.markdown(f"### 👤 {st.session_state.name}")
    m, s = divmod(int(rem.total_seconds()), 60)
    c2.markdown(f"<div style='font-size:24px; color:red; background:white; padding:10px; border-radius:10px; text-align:center;'>⏳ {m:02d}:{s:02d}</div>", unsafe_allow_html=True)

    user_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        st.markdown(f"**{i+1}. {q}**")
        ans = st.radio(f"Выбор {i}", opts, key=f"q_{i}", index=None, label_visibility="collapsed")
        user_ans.append(ans)

    if st.button("ЗАВЕРШИТЬ ТЕСТ ✅"):
        if None in user_ans: 
            st.error("Ответьте на все вопросы!")
        else:
            st.session_state.user_ans = user_ans
            st.session_state.test_state = "finishing"
            st.rerun()

# --- ЭКРАН 4: ИТОГИ ---
elif st.session_state.test_state == "finishing":
    # Код подсчета баллов и сохранения (как в вашем оригинале)
    # ... (просто скопируйте свой блок финиша сюда)
    st.write("Тест завершен. Результаты сохранены.")
    if st.button("На главную"):
        st.session_state.test_state = "login"
        st.rerun()
