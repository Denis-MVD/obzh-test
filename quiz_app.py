import streamlit as st
import random
from datetime import datetime
import pandas as pd
import os

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="НВП: Система тестирования", layout="centered", page_icon="🎖️")

# --- 2. ПАРАМЕТРЫ ---
TEACHER_PIN = "1234"
RESULTS_FILE = "detailed_results.csv"

def save_result_to_file(data):
    file_exists = os.path.isfile(RESULTS_FILE)
    df = pd.DataFrame([data])
    df.to_csv(RESULTS_FILE, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')

# --- 3. ДИЗАЙН (CSS) - УЛУЧШЕННАЯ ЧИТАЕМОСТЬ ---
st.markdown("""
    <style>
    /* Фон всей страницы */
    .stApp { 
        background-color: #e8e8e8; 
    }
    
    /* Блоки Хаки (Вопросы и поля) */
    div[data-testid="stVerticalBlock"] > div { 
        background-color: #3d4432 !important; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 10px solid #2f3526 !important; 
        margin-bottom: 20px;
        box-shadow: 4px 4px 12px rgba(0,0,0,0.15);
    }

    /* ФИКС ТЕКСТА: Белый, жирный, курсив */
    h1, h2, h3, h4, h5, p, label, .stMarkdown, [data-testid="stMarkdownContainer"], .stRadio label {
        color: #ffffff !important; 
        font-family: 'Segoe UI', Tahoma, sans-serif; 
        font-style: italic !important; 
        font-weight: bold !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.9);
    }

    /* Заголовки вне блоков (на светлом фоне) */
    .stApp h1, .stApp h2, .stApp h3 {
        color: #2f3526 !important;
        text-shadow: none;
        font-style: normal !important;
    }

    /* Поля ввода (Инпуты) */
    input, select, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #1e1e1e !important; 
        color: #ffffff !important; 
        border: 1px solid #ffffff !important;
        border-radius: 6px;
    }
    
    /* Цвет текста в выпадающем списке */
    div[data-baseweb="select"] * {
        color: white !important;
    }

    /* Стилизация кнопок */
    .stButton>button { 
        background-color: #2f3526 !important; 
        color: #ffffff !important; 
        font-weight: bold; 
        font-style: italic !important;
        border: 2px solid #ffffff !important;
        border-radius: 8px;
        text-transform: uppercase;
        width: 100%;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #3d4432 !important;
        border-color: #f1f1f1 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. ОФОРМЛЕНИЕ (АВТОМАТ АК-74) ---
# Стабильная ссылка на белый принт АК-74
AK_IMAGE = "https://cdn.pixabay.com/photo/2016/11/27/21/42/ak-47-1864227_1280.png"
st.image(AK_IMAGE, width=550)
st.write("### Военно-технический зачет")

# --- 5. СОСТОЯНИЕ ТЕСТА ---
if 'test_started' not in st.session_state: st.session_state.test_started = False
if 'test_finished' not in st.session_state: st.session_state.test_finished = False

# --- 6. БАЗА ВОПРОСОВ ---
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

# --- 7. ЭКРАН 1: РЕГИСТРАЦИЯ ---
if not st.session_state.test_started and not st.session_state.test_finished:
    st.title("🎖️ ТЕСТИРОВАНИЕ: ОБЖ / НВП")
    
    name = st.text_input("Фамилия и Имя ученика:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    
    if st.button("ПРИСТУПИТЬ К ТЕСТУ 🚀"):
        if name:
            st.session_state.user_name = name
            st.session_state.user_class = u_class
            st.session_state.shuffled_q = random.sample(questions_nvp, len(questions_nvp))
            st.session_state.test_started = True
            st.rerun()
        else:
            st.error("Ошибка: Введите фамилию!")

    st.divider()
    with st.expander("📊 ПАНЕЛЬ УЧИТЕЛЯ"):
        pin = st.text_input("Введите ПИН-код:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                df_res = pd.read_csv(RESULTS_FILE)
                st.write("Последние результаты:")
                st.dataframe(df_res[["Дата", "ФИО", "Класс", "Баллы"]])
                
                csv = df_res.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button("📥 СКАЧАТЬ ВЕДОМОСТЬ", data=csv, file_name="results.csv", mime="text/csv")

# --- 8. ЭКРАН 2: ПРОЦЕСС ТЕСТА ---
elif st.session_state.test_started:
    st.subheader(f"👤 Курсант: {st.session_state.user_name}")
    u_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.shuffled_q):
        st.markdown(f"**{i+1}. {q}**")
        ans = st.radio("Выберите ответ:", opts, key=f"q{i}", index=None)
        u_ans.append(ans)
    
    if st.button("ЗАВЕРШИТЬ И СДАТЬ ✅"):
        if None in u_ans: 
            st.warning("Ответьте на все вопросы!")
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

# --- 9. ЭКРАН 3: ИТОГИ ---
elif st.session_state.test_finished:
    st.header(f"ВАШ РЕЗУЛЬТАТ: {st.session_state.final_score} из {len(questions_nvp)}")
    st.write("### Подробный отчет:")
    for det in st.session_state.last_det:
        if "✅" in det: st.success(det)
        else: st.error(det)
    
    if st.button("ВЕРНУТЬСЯ НА ГЛАВНУЮ"):
        st.session_state.test_finished = False
        st.rerun()
