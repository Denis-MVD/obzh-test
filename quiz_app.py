import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import os
import base64
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# --- 1. ТЕХНИЧЕСКИЕ ФУНКЦИИ (ФОН И ГРАФИКА) ---
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

# --- 2. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="НВП: Контроль и Обучение", layout="centered", page_icon="🎖️")
set_png_as_page_bg('background.png')

# --- 3. КОНСТАНТЫ И ПУТИ ---
TEACHER_PIN = "1234"
RESULTS_FILE = "detailed_results.csv"
TEST_DURATION_MIN = 15
IMG_DIR = "фото" # Твоя папка на GitHub

# --- 4. ДАННЫЕ (ТВОИ ВОПРОСЫ) ---
questions_10 = [
    ("Что сделать при сигнале «Внимание всем!»?", ["Бежать на улицу", "Включить ТВ или радио", "Спрятаться в подвале", "Позвонить родным"], "Включить ТВ или радио"),
    ("Безопасное место в здании при землетрясении?", ["У окна", "В лифте", "Проем капитальных стен", "Угловая комната"], "Проем капитальных стен"),
    ("Землетрясение на улице. Где находиться?", ["У высокого здания", "Под ЛЭП", "На открытой площадке", "В машине"], "На открытой площадке"),
    ("Что такое сель?", ["Лавина", "Грязекаменный поток", "Толчок", "Ветер"], "Грязекаменный поток"),
    ("Действия при угрозе селя?", ["На дерево", "В сторону, перпендикулярно потоку", "Вниз по долине", "В доме"], "В сторону, перпендикулярно потоку"),
    ("Укрытие при урагане в поле?", ["Под деревом", "В кювете или овраге", "За щитом", "На мосту"], "В кювете или овраге"),
    ("Безопасная дистанция от упавших проводов ЛЭП?", ["2 м", "5 м", "8-10 м", "1 м"], "8-10 м"),
    ("Первое в «тревожном чемодане»?", ["Документы, вода, аптечка", "Ноутбук", "Одежда и книги", "Посуда"], "Документы, вода, аптечка"),
    ("Движение в зоне затопления?", ["Вплавь", "Медленно, проверяя путь палкой", "Бегом", "На лодке"], "Медленно, проверяя путь палкой"),
    ("Выход из лесного пожара:", ["По ветру", "Против ветра, перпендикулярно кромке", "Вглубь", "На месте"], "Против ветра, перпендикулярно кромке"),
    ("Главный фактор землетрясения?", ["Цунами", "Разрушение зданий", "Град", "Гроза"], "Разрушение зданий"),
    ("Вы в завале. Ваши действия?", ["Кричать постоянно", "Подавать сигналы стуком", "Резко выбираться", "Спичку зажечь"], "Подавать сигналы стуком"),
    ("Пожар в школе. Первое действие?", ["Урок продолжать", "Эвакуация и вызов 101", "Тушить самому", "Окна открыть"], "Эвакуация и вызов 101"),
    ("Эвакуация при пожаре:", ["Лифт", "Лестница", "Окно", "Под парту"], "Лестница"),
    ("Место в квартире при урагане?", ["Балкон", "Ванная или коридор", "Кухня", "У окна"], "Ванная или коридор")
]

questions_11 = [
    ("Авария на АЭС. Первое действие?", ["Балкон", "Йодная профилактика и герметизация", "Уехать", "Окна открыть"], "Йодная профилактика и герметизация"),
    ("Сигнал «Воздушная тревога»:", ["Наводнение", "Угроза оружия противника", "Пожар", "Землетрясение"], "Угроза оружия противника"),
    ("Герметизация при хим. аварии:", ["Закрыть окна, заклеить щели", "Кондиционер", "Вентиляция", "Огонь"], "Закрыть окна, заклеить щели"),
    ("Разлив ртути. Что делать?", ["Смыть водой", "Пылесос", "Вызвать спецов, проветрить", "Веник"], "Вызвать спецов, проветрить"),
    ("Сообщение о терроризме:", ["Игнор", "Полиция, не трогать предметы", "Сам осмотрю", "Открыть"], "Полиция, не трогать предметы"),
    ("Коллективные средства защиты:", ["Противогаз", "Убежища и укрытия", "Аптечка", "Респиратор"], "Убежища и укрытия"),
    ("Задача Гражданской обороны:", ["Парады", "Защита населения в ЧС и военное время", "Дороги", "Граница"], "Защита населения в ЧС и военное время"),
    ("Движение по зараженной зоне:", ["Быстро, без пыли", "Бегом", "Лечь", "Ягоды"], "Быстро, без пыли"),
    ("Защита органов дыхания:", ["Плащ", "Ватно-марлевая повязка", "Перчатки", "Очки"], "Ватно-марлевая повязка"),
    ("Эвакуация — это:", ["Прогулка", "Организованный вывоз в безопасную зону", "Бегство", "Дача"], "Организованный вывоз в безопасную зону"),
    ("АХОВ на коже. Действие?", ["Растереть", "Промыть водой", "Пластырь", "Ничего"], "Промыть водой"),
    ("Здание может рухнуть. Действие?", ["Вещи искать", "Лестница", "Лифт", "Балкон"], "Лестница"),
    ("Признак радиации:", ["Запах", "Звук", "Нет (только приборами)", "Свет"], "Нет (только приборами)"),
    ("НЕ фактор ядерного взрыва:", ["Ударная волна", "Световое излучение", "Сель", "Радиация"], "Сель"),
    ("Защита от аммиака. Повязку мочат:", ["Содой", "Лимонной кислотой", "Спиртом", "Маслом"], "Лимонной кислотой")
]

# --- 5. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
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

# --- 6. ЛОГИКА И ИНТЕРФЕЙС ---
if 'test_state' not in st.session_state: st.session_state.test_state = "login"

# ДИЗАЙН ТЕКСТА
st.markdown("""<style> h1, h2, h3, p, label { color: white !important; font-style: italic; text-shadow: 2px 2px 4px black; } </style>""", unsafe_allow_html=True)

# ЭКРАН 1: ЛОГИН
if st.session_state.test_state == "login":
    st.markdown("<h1 style='text-align: center;'>🎖️ ЗАЧЕТ ПО НВП: ГО</h1>", unsafe_allow_html=True)
    name = st.text_input("Фамилия и Имя:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    if st.button("ПЕРЕЙТИ К УРОКУ 📖"):
        if name:
            st.session_state.name, st.session_state.u_class = name, u_class
            st.session_state.test_state = "lesson"
            st.rerun()

# ЭКРАН 2: УРОК (ФОТО ЗДЕСЬ)
elif st.session_state.test_state == "lesson":
    st.markdown(f"## 📖 Изучение материала: {st.session_state.u_class}")
    
    # Фото 1
    col_img = os.path.join(IMG_DIR, "collage.jpg")
    if os.path.exists(col_img):
        st.image(col_img, caption="Основные виды ЧС (Сель, Пожар, Землетрясение)")
    
    # Фото 2
    info_img = os.path.join(IMG_DIR, "infografika.jpg")
    if os.path.exists(info_img):
        st.image(info_img, caption="Инструкция по выживанию в дверном проеме")

    st.info("Внимательно изучите изображения выше. Вопросы в тесте будут основаны на этих данных.")
    if st.button("ВСЕ ПОНЯТНО, НАЧАТЬ ТЕСТ 🚀"):
        st.session_state.start_time = datetime.now()
        raw_q = questions_10 if st.session_state.u_class == "10 класс" else questions_11
        st.session_state.questions = random.sample(raw_q, len(raw_q))
        st.session_state.test_state = "testing"
        st.rerun()

# ЭКРАН 3: ТЕСТ
elif st.session_state.test_state == "testing":
    st_autorefresh(interval=5000, key="timer")
    rem = timedelta(minutes=TEST_DURATION_MIN) - (datetime.now() - st.session_state.start_time)
    
    if rem.total_seconds() <= 0:
        st.session_state.test_state = "finishing"
        st.rerun()

    m, s = divmod(int(rem.total_seconds()), 60)
    st.markdown(f"### ⏳ Оставшееся время: {m:02d}:{s:02d}")
    
    user_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        st.write(f"**{i+1}. {q}**")
        ans = st.radio(f"Ответ {i}", opts, key=f"q_{i}", index=None, label_visibility="collapsed")
        user_ans.append(ans)

    if st.button("СДАТЬ РАБОТУ ✅"):
        if None in user_ans: st.error("Ответьте на все вопросы!")
        else:
            st.session_state.user_ans = user_ans
            st.session_state.test_state = "finishing"
            st.rerun()

# ЭКРАН 4: ИТОГИ
elif st.session_state.test_state == "finishing":
    score = sum(1 for i, (_, _, corr) in enumerate(st.session_state.questions) if st.session_state.user_ans[i] == corr)
    total = len(st.session_state.questions)
    grade = get_grade(score, total)
    
    st.markdown(f"## Итог: {score}/{total} ({grade})")
    save_result_to_file({"Дата": datetime.now().strftime("%d.%m %H:%M"), "ФИО": st.session_state.name, "Оценка": grade})
    if st.button("Выход"):
        st.session_state.test_state = "login"
        st.rerun()
