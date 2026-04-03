import streamlit as st
import random
from datetime import datetime
import pandas as pd
import os

# 1. Настройка страницы
st.set_page_config(page_title="ОБЖ: Система контроля", layout="centered", page_icon="🎖️")

# --- НАСТРОЙКИ ---
TEACHER_PIN = "1234"
RESULTS_FILE = "detailed_results.csv"

# Функция сохранения (теперь сохраняем и детализацию ответов)
def save_result_to_file(data):
    file_exists = os.path.isfile(RESULTS_FILE)
    df = pd.DataFrame([data])
    df.to_csv(RESULTS_FILE, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')

# --- ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f0f4f0; background-image: url("https://www.transparenttextures.com/patterns/pinstriped-suit.png"); }
    div[data-testid="stVerticalBlock"] > div { background-color: #ffffff !important; padding: 15px; border-radius: 10px; border-left: 5px solid #4b5320; margin-bottom: 10px; }
    .stTable td { color: black !important; }
    .stTable th { background-color: #4b5320 !important; color: white !important; }
    .stButton>button { background-color: #4b5320 !important; color: white !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 2. Инициализация
if 'test_started' not in st.session_state: st.session_state.test_started = False
if 'test_finished' not in st.session_state: st.session_state.test_finished = False

# --- БАЗА ВОПРОСОВ ---
questions_10 = [
    ("Первое действие при сигнале 'Внимание всем!'?", ["Бежать на улицу", "Включить ТВ или радио", "Выключить свет"], "Включить ТВ или радио"),
    ("Где безопаснее всего в здании при землетрясении?", ["В лифте", "У окна", "В дверном проеме капитальных стен"], "В дверном проеме капитальных стен"),
    ("Что делать, если наводнение застало вас в лесу?", ["Забраться на дерево", "Выйти на открытую поляну", "Спуститься к реке"], "Забраться на дерево"),
    ("Безопасное место в квартире при урагане?", ["Балкон", "Ванная комната или коридор", "Кухня у окна"], "Ванная комната или коридор"),
    ("Как двигаться в зоне лесного пожара?", ["По направлению ветра", "Против ветра", "Остаться на месте"], "Против ветра"),
    ("Что делать в снежной лавине?", ["Кричать", "Делать плавательные движения", "Сгруппироваться"], "Делать плавательные движения"),
    ("Признак приближения цунами?", ["Резкий отлив воды", "Сильный дождь", "Туман"], "Резкий отлив воды"),
    ("Защита дыхания при пепле?", ["Мокрая повязка", "Сухое полотенце", "Ничего"], "Мокрая повязка"),
    ("Где нельзя прятаться при грозе?", ["В кустах", "Под одиноким деревом", "В яме"], "Под одиноким деревом"),
    ("Что в 'тревожном чемодане'?", ["Документы, вода, еда", "Ноутбук, книги", "Посуда"], "Документы, вода, еда"),
    ("Угроза обвала в горах?", ["Бежать вниз", "Уйти в сторону", "Спрятаться"], "Уйти в сторону"),
    ("Подготовка дома к наводнению?", ["Открыть окна", "Вещи на чердак", "Ничего"], "Перенести ценные вещи на чердак"),
    ("Действие после землетрясения?", ["Зайти в дом", "Проверить газ", "Включить свет"], "Проверить газ"),
    ("Бедствие после землетрясения в море?", ["Смерч", "Цунами", "Метель"], "Цунами"),
    ("Расстояние от упавшего столба ЛЭП?", ["3 метра", "8-10 метров", "1 метр"], "8-10 метров")
]
# Аналогично для 11 класса (для краткости используем те же вопросы или добавьте свои)
questions_11 = questions_10 

# --- ЭКРАН 1: ВХОД ---
if not st.session_state.test_started and not st.session_state.test_finished:
    st.title("🎖️ Военно-технический зачет")
    name = st.text_input("Фамилия и Имя:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    
    if st.button("НАЧАТЬ ТЕСТ 🚀"):
        if name:
            st.session_state.user_name = name
            st.session_state.user_class = u_class
            st.session_state.shuffled_q = random.sample(questions_10 if u_class=="10 класс" else questions_11, 15)
            st.session_state.test_started = True
            st.rerun()

    st.divider()
    with st.expander("📊 ВХОД ДЛЯ УЧИТЕЛЯ"):
        pin = st.text_input("ПИН-код:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                df_res = pd.read_csv(RESULTS_FILE)
                st.write("### Сводная ведомость")
                st.table(df_res[["Дата", "ФИО", "Класс", "Баллы"]])
                
                st.write("### Подробный просмотр ответов")
                selected_user = st.selectbox("Выберите ученика для проверки:", df_res["ФИО"].unique())
                user_data = df_res[df_res["ФИО"] == selected_user].iloc[-1]
                
                # Восстанавливаем детализацию из строки
                details = user_data["Детализация"].split("|")
                for det in details:
                    if "✅" in det: st.success(det)
                    else: st.error(det)
            else: st.info("Данных пока нет.")

# --- ЭКРАН 2: ТЕСТ ---
elif st.session_state.test_started:
    st.subheader(f"🪖 Курсант: {st.session_state.user_name}")
    u_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.shuffled_q):
        st.info(f"**{i+1}.** {q}")
        ans = st.radio("Ответ:", opts, key=f"q{i}", index=None)
        u_ans.append(ans)
    
    if st.button("СДАТЬ РАБОТУ ✅"):
        if None in u_ans: st.warning("Ответьте на все вопросы!")
        else:
            score = 0
            det_list = []
            for i, (q, opts, corr) in enumerate(st.session_state.shuffled_q):
                if u_ans[i] == corr:
                    score += 1
                    det_list.append(f"✅ Вопрос {i+1}: Верно ({corr})")
                else:
                    det_list.append(f"❌ Вопрос {i+1}: Ошибка. Ответ: {u_ans[i]}. Правильно: {corr}")
            
            save_result_to_file({
                "Дата": datetime.now().strftime("%d.%m %H:%M"),
                "ФИО": st.session_state.user_name,
                "Класс": st.session_state.user_class,
                "Баллы": f"{score}/15",
                "Детализация": "|".join(det_list)
            })
            st.session_state.final_score = score
            st.session_state.last_det = det_list
            st.session_state.test_started = False
            st.session_state.test_finished = True
            st.rerun()

# --- ЭКРАН 3: РЕЗУЛЬТАТ И ОШИБКИ ---
elif st.session_state.test_finished:
    st.header(f"Ваш результат: {st.session_state.final_score} из 15")
    for det in st.session_state.last_det:
        if "✅" in det: st.success(det)
        else: st.error(det)
    if st.button("В НАЧАЛО"):
        st.session_state.test_finished = False
        st.rerun()
