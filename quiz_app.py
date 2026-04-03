import streamlit as st
import random
from datetime import datetime
import pandas as pd
import os

# --- 1. АВТОМАТ АК-74 (Верхний декоративный элемент) ---
# Мы размещаем изображение до настройки страницы, чтобы оно было самым первым элементом.
# URL изображения АК-74 с прозрачным фоном (PNG)
AK74_IMAGE_URL = "https://w7.pngwing.com/pngs/309/271/png-transparent-ak-74-kalashnikov-rifle-assault-rifle-weapon-rifle-ak47-assault-rifle-ammunition-thumbnail.png"

# Отображаем верхний автомат. centered=True выравнивает по центру.
st.image(AK74_IMAGE_URL, caption="Итоговый контроль знаний", use_column_width=False, width=400)


# --- 2. Настройка страницы ---
st.set_page_config(page_title="НВП: Система тестирования", layout="centered", page_icon="🎖️")


# --- НАСТРОЙКИ ---
TEACHER_PIN = "1234" # Стандартный ПИН-код
RESULTS_FILE = "detailed_results.csv"

def save_result_to_file(data):
    file_exists = os.path.isfile(RESULTS_FILE)
    df = pd.DataFrame([data])
    df.to_csv(RESULTS_FILE, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')


# --- 3. ДИЗАЙН (CSS) - СОВРЕМЕННЫЙ МИЛИТАРИ ---
# Оставляем вашу гармоничную тактическую палитру
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
        text-shadow: 1px 1px 1px rgba(0,0,0,0.5); /* Добавил легкую тень для объема */
    }

    /* Исключение для главных заголовков на светлом фоне (он должен быть темным) */
    .stApp h1, .stApp h3 {
        color: #2f3526 !important; 
        font-style: normal !important;
        text-shadow: none;
    }

    /* 4. Поля ввода (Темно-серый фон, белый шрифт) */
    input, select, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #2b2b2b !important; 
        color: #ffffff !important; 
        border: 1px solid #3d4432 !important;
        border-radius: 5px;
    }
    
    /* Цвет текста внутри выпадающего списка (в самом меню) */
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
    
    /* Таблицы и инфо-блоки (таблица теперь белая для контраста) */
    .stTable { background-color: #ffffff; border-radius: 10px; color: black !important;}
    .stTable th { background-color: #3d4432 !important; color: white !important;}
    
    /* Иконки успеха/ошибки */
    .stSuccess, .stError { color: white !important; }
    </style>
""", unsafe_allow_html=True)


# --- 4. Инициализация состояний ---
if 'test_started' not in st.session_state: st.session_state.test_started = False
if 'test_finished' not in st.session_state: st.session_state.test_finished = False


# --- 5. БАЗА ВОПРОСОВ ---
# Вопросы про гражданскую оборону и калибр автомата (8 самых важных)
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


# --- 6. ЭКРАН 1: ВХОД (РЕГИСТРАЦИЯ) ---
if not st.session_state.test_started and not st.session_state.test_finished:
    st.title("🎖️ ЗАЧЕТ ПО КУРСУ НВП / ОБЖ")
    
    name = st.text_input("Фамилия и Имя ученика:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    
    if st.button("НАЧАТЬ ТЕСТИРОВАНИЕ 🚀"):
        if name:
            st.session_state.user_name = name
            st.session_state.user_class = u_class
            # Перемешиваем вопросы (берем все 8)
            st.session_state.shuffled_q = random.sample(questions_nvp, len(questions_nvp))
            st.session_state.test_started = True
            st.rerun()
        else:
            st.error("Пожалуйста, введите фамилию!")

    st.divider()
    with st.expander("📊 ДЛЯ ПРЕПОДАВАТЕЛЯ (ПИН-КОД)"):
        pin = st.text_input("Код доступа:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                df_res = pd.read_csv(RESULTS_FILE)
                st.write("### *Сводная ведомость*")
                # Таблица теперь белая, поэтому текст черный
                st.table(df_res[["Дата", "ФИО", "Класс", "Баллы"]])
                
                # Кнопка скачивания
                csv_data = df_res.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("📥 СКАЧАТЬ ВЕДОМОСТЬ (EXCEL)", data=csv_data, file_name="results.csv", mime="text/csv")
            else:
                st.info("Данных пока нет.")


# --- 7. ЭКРАН 2: ТЕСТ ---
elif st.session_state.test_started:
    st.subheader(f"👤 Ученик: *{st.session_state.user_name}*")
    st.write("### *ОТВЕТИТЬ НА ВОПРОСЫ*")
    u_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.shuffled_q):
        # Вопросы на хаки фоне, текст белый курсив
        st.markdown(f"<p style='color:#f8f9fa !important; font-style:italic !important; font-size:1.1rem;'>**{i+1}. {q}**</p>", unsafe_allow_html=True)
        ans = st.radio("ВАШ ВЫБОР:", opts, key=f"q{i}", index=None)
        u_ans.append(ans)
    
    if st.button("ОТПРАВИТЬ РЕЗУЛЬТАТЫ ✅"):
        if None in u_ans: 
            st.warning("Внимание! Ответьте на все вопросы.")
        else:
            score = 0
            det_list = []
            for i, (q, opts, corr) in enumerate(st.session_state.shuffled_q):
                if u_ans[i] == corr:
                    score += 1
                    det_list.append(f"✅ Вопрос {i+1}: Верно")
                else:
                    det_list.append(f"❌ Вопрос {i+1}: Ошибка (Правильно: {corr})")
            
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


# --- 8. ЭКРАН 3: РЕЗУЛЬТАТ И ОШИБКИ ---
elif st.session_state.test_finished:
    st.header(f"ИТОГ: {st.session_state.final_score} ИЗ {len(questions_nvp)}")
    st.write("### *РАЗБОР ВАШИХ ОТВЕТОВ:*")
    for det in st.session_state.last_det:
        if "✅" in det: st.success(det)
        else: st.error(det)
    
    # --- НИЖНИЙ ДЕКОРАТИВНЫЙ ЭЛЕМЕНТ (Автомат #2) ---
    st.image(AK74_IMAGE_URL, caption="Зачет завершен. Вольно!", use_column_width=False, width=300)
    
    if st.button("В НАЧАЛО"):
        st.session_state.test_finished = False
        st.rerun()
