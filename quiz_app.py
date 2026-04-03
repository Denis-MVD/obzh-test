import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Настройки стиля
st.set_page_config(page_title="Зачет НВП", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f0f2f0; }
    html, body, [class*="css"] { font-family: 'Courier New', Courier, monospace; color: #1b261b; }
    div.stButton > button { background-color: #486348 !important; color: white !important; font-weight: bold; width: 100%; border-radius: 5px; }
    div.stButton > button:hover { background-color: #2b3d2b !important; color: #ffd700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎖️ ИТОГОВЫЙ ЗАЧЕТ ПО НВП")

# Сбор данных в боковой панели
with st.sidebar:
    st.header("Регистрация")
    name = st.text_input("ФИО ученика")
    group = st.text_input("Класс")
    st.divider()
    pin = st.text_input("Вход для учителя (ПИН)", type="password")

# Вопросы
questions = [
    {"q": "Калибр АК-74?", "a": ["5.45 мм", "7.62 мм", "9 мм"], "correct": "5.45 мм"},
    {"q": "Верхняя одежда военнослужащего?", "a": ["Китель", "Пальто", "Плащ"], "correct": "Китель"}
]

if name and group:
    st.success(f"Боец: {name}, Класс: {group}")
    ans = []
    for i, item in enumerate(questions):
        res = st.radio(item["q"], item["a"], key=i)
        ans.append(res)

    if st.button("СДАТЬ ТЕСТ"):
        score = sum(1 for i, item in enumerate(questions) if ans[i] == item["correct"])
        percent = (score / len(questions)) * 100
        grade = "5" if percent >= 90 else "4" if percent >= 70 else "3" if percent >= 50 else "2"
        
        # Сохранение
        res_data = {"Дата": datetime.now().strftime("%d.%m.%Y"), "ФИО": name, "Класс": group, "Оценка": grade}
        df = pd.DataFrame([res_data])
        df.to_csv("results.csv", mode='a', header=not os.path.exists("results.csv"), index=False)
        
        st.header(f"Ваша оценка: {grade}")
        st.balloons()

# Админка
if pin == "1234":
    st.header("📊 Ведомость")
    if os.path.exists("results.csv"):
        df_show = pd.read_csv("results.csv")
        st.table(df_show)
        st.download_button("Скачать ведомость", df_show.to_csv(index=False).encode('utf-8-sig'), "results.csv", "text/csv")
    else:
        st.info("Данных пока нет")
