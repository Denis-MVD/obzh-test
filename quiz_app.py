import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import os
import base64
from streamlit_autorefresh import st_autorefresh

# --- 1. УЛУЧШЕННАЯ ФУНКЦИЯ СТИЛЯ (ЗАЩИТА ОТ ЧЕРНОГО ЭКРАНА) ---
def set_page_style(file_path):
    bin_str = get_base64_of_bin_file(file_path)
    
    # Если файл найден — ставим его, если нет — просто темный цвет
    bg_css = f'background-image: url("data:image/png;base64,{bin_str}");' if bin_str else "background-color: #2b3023;"
    
    st.markdown(f'''
    <style>
    .stApp {{
        {bg_css}
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* БЛОКИРОВКА КОПИРОВАНИЯ (ПК + МОБИЛЬНЫЕ) */
    * {{
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
        user-select: none !important;
        -webkit-touch-callout: none !important;
    }}
    
    /* Разрешаем ввод в поля ФИО */
    input, textarea, [data-baseweb="input"] {{
        -webkit-user-select: text !important;
        user-select: text !important;
    }}

    /* ДИЗАЙН КОНТЕЙНЕРОВ (ВАША СТРУКТУРА) */
    div[data-testid="stVerticalBlock"] > div {{
        background-color: rgba(61, 68, 50, 0.9) !important;
        padding: 20px; 
        border-radius: 15px; 
        border-left: 10px solid #1a1e15 !important;
        margin-bottom: 15px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }}

    h1, h2, h3, p, label {{
        color: #ffffff !important;
        font-family: 'Segoe UI', sans-serif;
        text-shadow: 2px 2px 4px #000;
    }}
    
    hr {{ border: 1px solid rgba(255,255,255,0.3); }}
    </style>
    
    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    </script>
    ''', unsafe_allow_html=True)

def get_base64_of_bin_file(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

# --- 2. НАСТРОЙКИ ---
st.set_page_config(page_title="НВП: Контроль", layout="centered")
set_page_style('background.png') # Убедитесь, что файл в GitHub называется именно так

TEACHER_PIN = "1234"
RESULTS_FILE = "detailed_results.csv"

# --- 3. ВОПРОСЫ ---
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

# --- 4. СОСТОЯНИЯ ---
if 'test_state' not in st.session_state: st.session_state.test_state = "login"

# --- ЭКРАН 1: ЛОГИН ---
if st.session_state.test_state == "login":
    st.markdown("<p style='text-align: center; margin-bottom: -15px;'>Преподаватель Начальной военной и технической подготовки</p>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<p style='text-align: center; margin-bottom: -15px;'>Семенков Денис Алексеевич</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("<h1 style='text-align: center;'>🎖️ ЗАЧЕТ ПО НВП: ГРАЖДАНСКАЯ ОБОРОНА</h1>", unsafe_allow_html=True)
    
    name = st.text_input("Введите Фамилию и Имя:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    
    if st.button("ПЕРЕЙТИ К ОБУЧЕНИЮ 📖"):
        if name:
            st.session_state.name, st.session_state.u_class = name, u_class
            st.session_state.test_state = "lesson"
            st.rerun()

    with st.expander("📊 КАБИНЕТ ПРЕПОДАВАТЕЛЯ"):
        pin = st.text_input("PIN:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                st.dataframe(pd.read_csv(RESULTS_FILE), use_container_width=True)

# --- ЭКРАН 2: УРОК ---
elif st.session_state.test_state == "lesson":
    st.markdown(f"## 📖 Учебный материал: {st.session_state.u_class}")
    if os.path.exists("collage.jpg"):
        st.image("collage.jpg", use_container_width=True)
    
    st.info("Внимательно изучите изображения. Копирование текста заблокировано.")
    if st.button("НАЧАТЬ ТЕСТИРОВАНИЕ 🚀"):
        st.session_state.start_time = datetime.now()
        raw_q = questions_10 if st.session_state.u_class == "10 класс" else questions_11
        st.session_state.questions = random.sample(raw_q, len(raw_q))
        st.session_state.test_state = "testing"
        st.rerun()

# --- ЭКРАН 3: ТЕСТ ---
elif st.session_state.test_state == "testing":
    st_autorefresh(interval=5000, key="timer")
    rem = timedelta(minutes=15) - (datetime.now() - st.session_state.start_time)
    
    if rem.total_seconds() <= 0:
        st.session_state.test_state = "finishing"
        st.rerun()

    st.write(f"👤 {st.session_state.name} | ⏳ Время: {int(rem.total_seconds()//60)} мин.")
    
    user_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        st.markdown(f"**{i+1}. {q}**")
        ans = st.radio(f"Ответ {i}", opts, key=f"q_{i}", index=None)
        user_ans.append(ans)

    if st.button("ЗАВЕРШИТЬ ТЕСТ ✅"):
        if None in user_ans: st.warning("Ответьте на все вопросы!")
        else:
            st.session_state.user_ans = user_ans
            st.session_state.test_state = "finishing"
            st.rerun()

# --- ЭКРАН 4: ИТОГИ ---
elif st.session_state.test_state == "finishing":
    score = sum(1 for i, (_, _, corr) in enumerate(st.session_state.questions) if st.session_state.user_ans[i] == corr)
    st.markdown(f"# Результат: {score} из {len(st.session_state.questions)}")
    
    if st.button("В НАЧАЛО"):
        st.session_state.test_state = "login"
        st.rerun()
