import streamlit as st
import random
from datetime import datetime
import pandas as pd
import os

# 1. Настройка страницы
st.set_page_config(page_title="НВП: Система тестирования", layout="centered", page_icon="🎖️")

# --- НАСТРОЙКИ ---
TEACHER_PIN = "1234"
RESULTS_FILE = "detailed_results.csv"

def save_result_to_file(data):
    file_exists = os.path.isfile(RESULTS_FILE)
    df = pd.DataFrame([data])
    df.to_csv(RESULTS_FILE, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')

# --- ДИЗАЙН (CSS) - СОВРЕМЕННЫЙ МИЛИТАРИ ---
st.markdown("""
    <style>
    /* 1. Общий фон страницы (Светло-серый, нейтральный) */
    .stApp { 
        background-color: #e8e8e8; 
    }
    
    /* 2. Блоки с вопросами: ТЕМНО-ОЛИВКОВЫЙ (ХАКИ) */
    div[data-testid="stVerticalBlock"] > div { 
        background-color: #3d4432 !important; /* Современный Хаки */
        padding: 25px; 
        border-radius: 10px; 
        border-left: 12px solid #2f3526 !important; /* Темный акцент слева */
        margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
    }

    /* 3. ШРИФТ: БЕЛЫЙ / КРЕМОВЫЙ, КУРСИВ, ЖИРНЫЙ */
    h1, h2, h3, h4, h5, p, label, .stMarkdown, [data-testid="stMarkdownContainer"], .stRadio label {
        color: #f8f9fa !important; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        font-style: italic !important; 
        font-weight: bold !important;
    }

    /* Исключение для главных заголовков на светлом фоне */
    .stApp h1, .stApp h3 {
        color: #2f3526 !important; 
        font-style: normal !important;
    }

    /* 4. Поля ввода (Темно-серый фон, белый шрифт) */
    input, select, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #2b2b2b !important; 
        color: #ffffff !important; 
        border: 1px solid #3d4432 !important;
        border-radius: 5px;
    }
    
    div[data-baseweb="select"] * {
        color: white !important;
    }

    /* 5. Кнопки: ТЕМНО-ОЛИВКОВЫЕ (СТИЛЬ "ТАКТИК") */
    .stButton>button { 
        background-color: #3d4432 !important; 
        color: #ffffff !important; 
        font-weight: bold; 
        font-style: italic !important;
        border: 2px solid #2f3526 !important;
        border-radius: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2f3526 !important;
        box-shadow: 0 0 10px rgba(0,0,0,0.3);
    }
    
    /* Таблицы и инфо-блоки */
    .stTable { background-color: #ffffff; border-radius: 10px; }
    .stSuccess, .stError { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Инициализация состояний
if 'test_started' not in st.session_state: st.session_state.test_started = False
if 'test_finished' not in st.session_state: st.session_state.test_finished = False

# --- БАЗА ВОПРОСОВ ---
questions_nvp = [
    ("Первое действие при сигнале 'Внимание всем!'?", ["Бежать на улицу", "Включить ТВ или радио", "Выключить свет"], "Включить ТВ или радио"),
    ("Где безопаснее всего в здании при землетрясении?", ["В лифте", "У окна", "В дверном проеме капитальных стен"], "В дверном проеме капитальных стен"),
    ("Что делать, если наводнение застало вас в лесу?", ["Забраться на дерево", "Выйти на открытую поляну", "Спуститься к реке"], "Забраться на дерево"),
    ("Безопасное место в квартире при урагане?", ["Балкон", "Ванная комната или коридор", "Кухня у окна"], "Ванная комната или коридор"),
    ("Калибр автомата АК-74?", ["7.62 мм", "5.45 мм", "9 мм", "5.56 мм"], "5.45 мм"),
    ("Что должно быть в 'тревожном чемодане'?", ["Документы, вода, еда", "Ноутбук, книги", "Посуда"], "Документы, вода, еда"),
    ("Безопасное расстояние от упавшего столба ЛЭП?", ["3 метра", "8-10 метров", "1 метр"], "8-10 метров"),
    ("Ваше действие при угрозе обвала в горах?", ["Бежать вниз", "Уйти в сторону", "Спрятаться под деревом"], "Уйти в сторону")
]

# --- ЭКРАН 1: ВХОД ---
if not st.session_state.test_started and not st.session_state.test_finished:
    st.title("🎖️ ЗАЧЕТ ПО КУРСУ НВП / ОБЖ")
    
    name = st.text_input("Фамилия и Имя ученика:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    
    if st.button("НАЧАТЬ ТЕСТИРОВАНИЕ 🚀"):
        if name:
            st.session_state.user_name = name
            st.session_state.user_class = u_class
            st.session_state.shuffled_q = random.sample(questions_nvp, len(questions_nvp))
            st.session_state.test_started = True
            st.rerun()
        else:
            st.error("Пожалуйста, введите фамилию!")

    st.divider()
    with st.expander("📊 ДЛЯ ПРЕПОДАВАТЕЛЯ"):
        pin = st.text_input("Код доступа:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                df_res = pd.read_csv(RESULTS_FILE)
                st.write("### Сводная ведомость")
                st.dataframe(df_res[["Дата", "ФИО", "Класс", "Баллы"]])
                
                csv_data = df_res.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("📥 СКАЧАТЬ ВЕДОМОСТЬ (CSV)", data=csv_data, file_name="results.csv", mime="text/csv")
            else:
                st.info("Данных пока нет.")

# --- ЭКРАН 2: ТЕСТ ---
elif st.session_state.test_started:
    st.subheader(f"👤 Ученик: {st.session_state.user_name}")
    u_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.shuffled_q):
        st.markdown(f"***{i+1}. {q}***")
        ans = st.radio("Выберите ответ:", opts, key=f"q{i}", index=None)
        u_ans.append(ans)
    
    if st.button("ОТПРАВИТЬ РЕЗУЛЬТАТЫ ✅"):
        if None in u_ans: 
            st.warning("Необходимо ответить на все вопросы!")
        else:
            score = 0
            det_list = []
            for i, (q, opts, corr) in enumerate(st.session_state.shuffled_q):
                if u_ans[i] == corr:
                    score += 1
                    det_list.append(f"✅ Вопрос {i+1}: Верно")
                else:
                    det_list.append(f"❌ Вопрос {i+1}: Ошибка (Верно: {corr})")
            
            save_result_to_file({
                "Дата": datetime.now().strftime("%d.%m %H:%M"),
                "ФИО": st.session_state.user_name,
                "Класс": st.session_state.user_class,
                "Баллы": f"{score}/{len(questions_nvp)}", 
                "Детализация": "|".join(det_list)
            })
            st.session_state.final_score = score
            st.session_state.last_det = det_list
            st.session_state.test_started = False
            st.session_state.test_finished = True
            st.rerun()

# --- ЭКРАН 3: РЕЗУЛЬТАТ ---
elif st.session_state.test_finished:
    st.header(f"Ваш результат: {st.session_state.final_score} из {len(questions_nvp)}")
    st.write("### Детализация:")
    for det in st.session_state.last_det:
        if "✅" in det: st.success(det)
        else: st.error(det)
    
    if st.button("ВЕРНУТЬСЯ К НАЧАЛУ"):
        st.session_state.test_finished = False
        st.rerun()
