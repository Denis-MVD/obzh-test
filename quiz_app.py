import streamlit as st
import random
from datetime import datetime
import pandas as pd
import os

# 1. Настройка страницы
st.set_page_config(page_title="НВП СССР: Контроль", layout="centered", page_icon="☭")

# --- НАСТРОЙКИ ---
TEACHER_PIN = "1945" # ПИН-код изменен на исторический
RESULTS_FILE = "detailed_results.csv"

# Функция сохранения
def save_result_to_file(data):
    file_exists = os.path.isfile(RESULTS_FILE)
    df = pd.DataFrame([data])
    df.to_csv(RESULTS_FILE, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')

# --- ДИЗАЙН (CSS) - СССР ВОЕННЫЙ СТИЛЬ ---
st.markdown("""
    <style>
    /* Общий фон страницы (светло-оливковый) */
    .stApp { 
        background-color: #f4f1e1; 
        background-image: url("https://www.transparenttextures.com/patterns/pinstriped-suit.png");
    }
    
    /* Стилизация блоков: КРАСНАЯ ПОЛОСА слева (как петлица/знамя) */
    div[data-testid="stVerticalBlock"] > div { 
        background-color: #fbf9f0 !important; 
        padding: 20px; 
        border-radius: 8px; 
        border-left: 10px solid #c80000 !important; /* Насыщенный красный СССР */
        margin-bottom: 15px;
        box-shadow: 3px 3px 6px rgba(0,0,0,0.2);
    }

    /* --- ГЛОБАЛЬНЫЕ СТИЛИ ШРИФТА --- */
    /* БЕЛЫЙ ШРИФТ В КУРСИВЕ для всего, где фон темный */
    h1, h2, h3, p, label, .stMarkdown, [data-testid="stMarkdownContainer"] {
        color: white !important; /* Принудительно белый */
        font-family: 'Courier New', Courier, monospace; /* Военный/печатная машинка */
        font-style: italic !important; /* Курсив */
        font-weight: bold !important; /* Жирный для читаемости */
        text-shadow: 1px 1px 2px black; /* Тень, чтобы не сливался на светлом */
    }

    /* Исключение для основного фона (чтобы заголовки на светлом были видны) */
    .stApp h1, .stApp h2, .stApp p {
        color: #1a2a1a !important; /* Темно-оливковый для заголовков на главном фоне */
        text-shadow: none;
    }

    /* СТИЛЬ ДЛЯ ТЕМНО-ЗЕЛЕНЫХ ПОЛЕЙ (заменяем черное) */
    /* Поле ввода имени и класс (selectbox) */
    .stTextInput>div>div>input, .stSelectbox>div>div>select, div[data-baseweb="select"] {
        background-color: #4b5320 !important; /* ТЕМНО-ЗЕЛЕНЫЙ ХАКИ */
        color: white !important; /* Белый шрифт внутри */
        border: 2px solid #3a411a !important;
        font-style: italic !important;
        border-radius: 5px;
    }
    
    /* Цвет текста внутри выпадающего списка */
    div[data-baseweb="select"] * {
        color: white !important;
    }
    
    /* Радиокнопки (варианты ответов) */
    .stRadio label {
        background-color: #556b2f !important; /* Светлее оливковый для вариантов */
        color: white !important;
        font-style: italic !important;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
    }

    /* Кнопка "Начать" / "Сдать" (Красная) */
    .stButton>button { 
        background-color: #a50000 !important; /* Красный заголовок */
        color: white !important; 
        font-weight: bold; 
        font-style: italic !important;
        width: 100%;
        border: 2px solid #800000;
        border-radius: 8px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .stButton>button:hover {
        background-color: #c80000 !important;
    }
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
    ("Что в 'тревожном чемодане'?", ["Документы, вода, еда", "Ноутбук, книги", "Посуда"], "Документы, вода, еда"),
    ("Расстояние от упавшего столба ЛЭП?", ["3 метра", "8-10 метров", "1 метр"], "8-10 метров"),
    ("Угроза обвала в горах?", ["Бежать вниз", "Уйти в сторону", "Спрятаться"], "Уйти в сторону")
]

# --- ЭКРАН 1: ВХОД (РЕГИСТРАЦИЯ) ---
if not st.session_state.test_started and not st.session_state.test_finished:
    st.title("☭ НВП СССР: ЗАЧЕТНАЯ ВЕДОМОСТЬ")
    st.markdown("### *ВВЕДИТЕ ДАННЫЕ ДЛЯ ДОПУСКА*")
    
    name = st.text_input("Фамилия и Имя Курсанта:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    
    if st.button("К СДАЧЕ ПРИСТУПИТЬ 🚀"):
        if name:
            st.session_state.user_name = name
            st.session_state.user_class = u_class
            # Перемешиваем 8 вопросов
            st.session_state.shuffled_q = random.sample(questions_nvp, 8)
            st.session_state.test_started = True
            st.rerun()
        else:
            st.error("Введите фамилию для идентификации!")

    st.divider()
    with st.expander("📊 ВХОД ДЛЯ ПРЕПОДАВАТЕЛЯ (ПИН)"):
        pin = st.text_input("Код доступа:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                df_res = pd.read_csv(RESULTS_FILE)
                st.write("### *Сводная ведомость зачетов*")
                st.dataframe(df_res[["Дата", "ФИО", "Класс", "Баллы"]])
                
                # Кнопка скачивания
                csv_data = df_res.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("📥 СКАЧАТЬ ВЕДОМОСТЬ (EXCEL)", data=csv_data, file_name="vedomost_nvp.csv", mime="text/csv")
            else:
                st.info("Результатов пока нет.")

# --- ЭКРАН 2: ТЕСТ ---
elif st.session_state.test_started:
    st.subheader(f"🪖 Курсант: *{st.session_state.user_name}*")
    st.markdown("### *ОТВЕТИТЬ НА ВОПРОСЫ*")
    u_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.shuffled_q):
        # Вопросы на светлом фоне, поэтому текст темно-зеленый
        st.markdown(f"<p style='color:#1a2a1a !important; font-style:italic !important;'>**{i+1}. {q}**</p>", unsafe_allow_html=True)
        ans = st.radio("Выберите вариант:", opts, key=f"q{i}", index=None)
        u_ans.append(ans)
    
    if st.button("СДАТЬ РАБОТУ ✅"):
        if None in u_ans: 
            st.warning("Внимание! Ответьте на все вопросы перед сдачей.")
        else:
            score = 0
            det_list = []
            for i, (q, opts, corr) in enumerate(st.session_state.shuffled_q):
                if u_ans[i] == corr:
                    score += 1
                    det_list.append(f"✅ Вопрос {i+1}: Верно")
                else:
                    det_list.append(f"❌ Вопрос {i+1}: Ошибка. Ваш ответ: {u_ans[i]}. Правильно: {corr}")
            
            save_result_to_file({
                "Дата": datetime.now().strftime("%d.%m %H:%M"),
                "ФИО": st.session_state.user_name,
                "Класс": st.session_state.user_class,
                "Баллы": f"{score}/8", # Изменил на 8 вопросов
                "Детализация": "|".join(det_list)
            })
            st.session_state.final_score = score
            st.session_state.last_det = det_list
            st.session_state.test_started = False
            st.session_state.test_finished = True
            st.rerun()

# --- ЭКРАН 3: РЕЗУЛЬТАТ ---
elif st.session_state.test_finished:
    st.header(f"Ваш результат: *{st.session_state.final_score}* из 8")
    st.write("### *Разбор ваших ответов:*")
    for det in st.session_state.last_det:
        if "✅" in det: st.success(det)
        else: st.error(det)
    
    if st.button("ВЕРНУТЬСЯ НА ГЛАВНУЮ"):
        st.session_state.test_finished = False
        st.rerun()
