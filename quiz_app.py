import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import os
import plotly.express as px
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
        /* Убираем стандартные элементы управления Streamlit, чтобы сложнее было выйти */
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

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="НВП: Контроль", layout="centered", page_icon="🎖️")
set_png_as_page_bg('background.png')

# --- 2. КОНСТАНТЫ ---
TEACHER_PIN = "1234"
RESULTS_FILE = "detailed_results.csv"
TEST_DURATION_MIN = 15 

# --- 3. ФУНКЦИИ ---
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

# --- 4. ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stMarkdownContainer"], .stRadio label {
        color: #ffffff !important; font-family: 'Segoe UI', sans-serif; 
        font-style: italic !important; font-weight: bold !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.9);
    }
    input, select, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #1a1a1a !important; color: white !important; border: 1px solid #ffffff !important;
    }
    .stButton>button { 
        background-color: #2f3526 !important; color: white !important; 
        font-weight: bold; border: 2px solid #ffffff !important; width: 100%;
    }
    .timer-box { font-size: 26px; color: #ff4b4b; font-weight: bold; text-align: center; background: rgba(255,255,255,0.9); padding: 10px; border-radius: 10px; border: 3px solid #2f3526; }
    </style>
""", unsafe_allow_html=True)

# --- 5. ВОПРОСЫ ---
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

# --- 6. ЛОГИКА СОСТОЯНИЙ ---
if 'test_state' not in st.session_state: st.session_state.test_state = "login"
if 'results_saved' not in st.session_state: st.session_state.results_saved = False

# --- 7. ЭКРАН 1: ВХОД ---
if st.session_state.test_state == "login":
    st.markdown("<h1 style='text-align: center; color: white;'>🎖️ ЗАЧЕТ ПО НВП: ГРАЖДАНСКАЯ ОБОРОНА</h1>", unsafe_allow_html=True)
    name = st.text_input("Фамилия и Имя ученика:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    if st.button("НАЧАТЬ ТЕСТИРОВАНИЕ 🚀"):
        if name:
            st.session_state.name = name
            st.session_state.u_class = u_class
            st.session_state.start_time = datetime.now()
            st.session_state.results_saved = False
            raw_q = questions_10 if u_class == "10 класс" else questions_11
            shuffled = []
            for q_text, opts, corr in random.sample(raw_q, len(raw_q)):
                sh_opts = random.sample(opts, len(opts))
                shuffled.append((q_text, sh_opts, corr))
            st.session_state.questions = shuffled
            st.session_state.test_state = "testing"
            st.rerun()

    with st.expander("📊 КАБИНЕТ ПРЕПОДАВАТЕЛЯ"):
        pin = st.text_input("PIN:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                df_all = pd.read_csv(RESULTS_FILE)
                st.dataframe(df_all, use_container_width=True)
                if st.button("🗑️ ОЧИСТИТЬ"):
                    os.remove(RESULTS_FILE)
                    st.rerun()

# --- 8. ЭКРАН 2: ТЕСТИРОВАНИЕ (БЛОКИРОВКА) ---
elif st.session_state.test_state == "testing":
    # Живой таймер каждые 5 сек
    st_autorefresh(interval=5000, key="timer_refresh")
    
    elapsed = datetime.now() - st.session_state.start_time
    rem = timedelta(minutes=TEST_DURATION_MIN) - elapsed
    
    if rem.total_seconds() <= 0:
        st.session_state.test_state = "finishing"
        st.rerun()

    c1, c2 = st.columns([2, 1])
    c1.markdown(f"### 👤 {st.session_state.name}")
    m, s = divmod(int(rem.total_seconds()), 60)
    c2.markdown(f"<div class='timer-box'>⏳ {m:02d}:{s:02d}</div>", unsafe_allow_html=True)

    # Запрещаем выходить из теста, пока он не закончен
    user_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        st.markdown(f"**{i+1}. {q}**")
        ans = st.radio(f"Выбор {i}", opts, key=f"q_{i}", index=None, label_visibility="collapsed")
        user_ans.append(ans)

    # Кнопка завершения - единственный легальный путь наружу
    if st.button("ЗАКОНЧИТЬ И ВЫЙТИ ✅"):
        if None in user_ans: 
            st.error("⚠️ ВНИМАНИЕ: Вы не ответили на все вопросы! Выход заблокирован.")
        else:
            st.session_state.user_ans = user_ans
            st.session_state.test_state = "finishing"
            st.rerun()

# --- 9. ЭКРАН 3: ИТОГИ ---
elif st.session_state.test_state == "finishing":
    score = 0
    total = len(st.session_state.questions)
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        if st.session_state.user_ans[i] == corr: score += 1
    
    grade = get_grade(score, total)
    if not st.session_state.results_saved:
        save_result_to_file({"Дата": datetime.now().strftime("%H:%M"), "ФИО": st.session_state.name, "Класс": st.session_state.u_class, "Баллы": f"{score}/{total}", "Оценка": grade})
        st.session_state.results_saved = True

    st.markdown(f"<h1 style='text-align: center; color: white;'>Результат: {score} из {total}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; color: gold;'>Оценка: {grade}</h2>", unsafe_allow_html=True)
    
    if st.button("ВЕРНУТЬСЯ К НАЧАЛУ"):
        st.session_state.test_state = "login"
        st.rerun()
