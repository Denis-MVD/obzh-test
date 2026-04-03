import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- НАСТРОЙКИ СТИЛЯ (ШРИФТ И ЦВЕТ) ---
st.set_page_config(page_title="Зачет по НВП", page_icon="🎖️")

st.markdown("""
    <style>
    /* Основной шрифт и фон */
    html, body, [class*="css"] {
        font-family: 'Courier New', Courier, monospace; 
        color: #1b261b;
    }
    
    /* Заголовок в армейском стиле */
    .stHeader h1 {
        color: #2d3e2d !important;
        text-transform: uppercase;
        border-bottom: 3px solid #486348;
        padding-bottom: 10px;
    }

    /* Кнопки: Цвет Хаки */
    div.stButton > button {
        background-color: #486348 !important;
        color: white !important;
        border: 2px solid #2b3d2b;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }

    /* Эффект при наведении */
    div.stButton > button:hover {
        background-color: #2b3d2b !important;
        color: #ffd700 !important;
        border-color: #ffd700;
    }

    /* Стиль для вопросов */
    .stRadio label {
        font-size: 18px !important;
        font-weight: bold;
        background: #f0f2f0;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ЛОГИКА ТЕСТА ---

# Список вопросов (можно добавлять свои)
questions = [
    {
        "question": "Калибр автомата АК-74?",
        "options": ["7.62 мм", "5.45 мм", "9.00 мм", "5.56 мм"],
        "answer": "5.45 мм"
    },
    {
        "question": "Что необходимо сделать в первую очередь при обнаружении кровотечения?",
        "options": ["Дать обезболивающее", "Наложить давящую повязку или жгут", "Промыть рану водой", "Вызвать полицию"],
        "answer": "Наложить давящую повязку или жгут"
    }
]

st.title("🎖️ Итоговый зачет по НВП / ОБЖ")

# Форма регистрации ученика
with st.sidebar:
    st.header("Данные бойца")
    student_name = st.text_input("ФИО ученика")
    student_class = st.text_input("Класс (например, 10А)")
    
    st.divider()
    # Секция для учителя (скрытая)
    teacher_pin = st.text_input("ПИН-код для ведомости", type="password")

if student_name and student_class:
    st.info(f"К сдаче зачета допущен: {student_name} ({student_class})")
    
    responses = []
    for i, q in enumerate(questions):
        st.subheader(f"Вопрос №{i+1}")
        res = st.radio(q["question"], q["options"], key=f"q{i}")
        responses.append(res)

    if st.button("ЗАВЕРШИТЬ ТЕСТ И ОТПРАВИТЬ ОТВЕТ"):
        # Считаем баллы
        score = 0
        for i, q in enumerate(questions):
            if responses[i] == q["answer"]:
                score += 1
        
        percent = (score / len(questions)) * 100
        
        # Оценка
        if percent >= 90: grade = "5"
        elif percent >= 75: grade = "4"
        elif percent >= 50: grade = "3"
        else: grade = "2"

        # Сохраняем результат
        new_data = {
            "Дата": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "ФИО": student_name,
            "Класс": student_class,
            "Баллы": score,
            "Процент": f"{percent}%",
            "Оценка": grade
        }
        
        df = pd.DataFrame([new_data])
        
        # Запись в файл (в Streamlit Cloud файлы временные, но для урока хватит)
        if not os.path.isfile("results.csv"):
            df.to_csv("results.csv", index=False)
        else:
            df.to_csv("results.csv", mode='a', header=False, index=False)
            
        st.success(f"Тест завершен! Ваша оценка: {grade}")
        st.balloons()

# --- СЕКЦИЯ УЧИТЕЛЯ ---
if teacher_pin == "1234":  # Ваш ПИН-код
    st.divider()
    st.header("📊 Ведомость результатов")
    if os.path.isfile("results.csv"):
        results_df = pd.read_csv("results.csv")
        st.dataframe(results_df)
        
        # Кнопка скачивания для учителя
        csv = results_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 СКАЧАТЬ ВЕДОМОСТЬ (EXCEL)",
            data=csv,
            file_name=f"vedomost_nvp_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
    else:
        st.warning("Результатов пока нет.")
else:
    if teacher_pin != "":
        st.error("Неверный ПИН-код доступа!")
