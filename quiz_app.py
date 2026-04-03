import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import os
import plotly.express as px

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="НВП: Система тестирования", layout="centered", page_icon="🎖️")

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
    .stApp { background-color: #e8e8e8; }
    div[data-testid="stVerticalBlock"] > div { 
        background-color: #3d4432 !important; 
        padding: 25px; border-radius: 10px; 
        border-left: 12px solid #2f3526 !important; margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.2);
    }
    h1, h2, h3, h4, p, label, .stMarkdown, [data-testid="stMarkdownContainer"], .stRadio label {
        color: #ffffff !important; font-family: 'Segoe UI', sans-serif; 
        font-style: italic !important; font-weight: bold !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    .stApp h1, .stApp h2 { color: #2f3526 !important; font-style: normal !important; text-shadow: none; margin-top: -30px; }
    input, select, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #2b2b2b !important; color: white !important; border: 1px solid white !important;
    }
    div[data-baseweb="select"] * { color: white !important; }
    .stButton>button { 
        background-color: #2f3526 !important; color: white !important; 
        font-weight: bold; border: 2px solid white !important; width: 100%;
    }
    .timer-box { font-size: 24px; color: #ff4b4b; font-weight: bold; text-align: center; background: white; padding: 10px; border-radius: 10px; border: 2px solid #2f3526; }
    </style>
""", unsafe_allow_html=True)

# --- 5. БАЗА ВОПРОСОВ ---
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

# --- 7. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЙ ---
if 'test_state' not in st.session_state: st.session_state.test_state = "login"
if 'results_saved' not in st.session_state: st.session_state.results_saved = False

# --- 8. ЭКРАН 1: ВХОД ---
if st.session_state.test_state == "login":
    st.title("🎖️ ЗАЧЕТ ПО НВП: ГРАЖДАНСКАЯ ОБОРОНА")
    name = st.text_input("Фамилия и Имя ученика:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    
    if st.button("НАЧАТЬ ТЕСТИРОВАНИЕ 🚀"):
        if name:
            st.session_state.name = name
            st.session_state.u_class = u_class
            st.session_state.start_time = datetime.now()
            st.session_state.results_saved = False # Сброс флага записи
            
            raw_q = questions_10 if u_class == "10 класс" else questions_11
            shuffled = []
            for q_text, opts, corr in random.sample(raw_q, len(raw_q)):
                sh_opts = random.sample(opts, len(opts)) # Рандом вариантов
                shuffled.append((q_text, sh_opts, corr))
            st.session_state.questions = shuffled
            st.session_state.test_state = "testing"
            st.rerun()
        else:
            st.error("Введите фамилию!")

    st.divider()
    with st.expander("📊 КАБИНЕТ ПРЕПОДАВАТЕЛЯ"):
        pin = st.text_input("Код доступа:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                df_all = pd.read_csv(RESULTS_FILE)
                if not df_all.empty and 'Оценка' in df_all.columns:
                    st.write("### Успеваемость")
                    counts = df_all['Оценка'].value_counts().reset_index()
                    counts.columns = ['Оценка', 'Кол-во']
                    fig = px.pie(counts, names='Оценка', values='Кол-во', hole=0.4, 
                                 color='Оценка', color_discrete_map={
                                     '5 (Отлично)':'#2ecc71','4 (Хорошо)':'#3498db',
                                     '3 (Удовл.)':'#f1c40f','2 (Неуд.)':'#e74c3c'})
                    st.plotly_chart(fig)
                    st.dataframe(df_all[["Дата", "ФИО", "Класс", "Баллы", "Оценка"]], use_container_width=True)
                    st.download_button("📥 СКАЧАТЬ ВЕДОМОСТЬ", df_all.to_csv(index=False).encode('utf-8-sig'), "results.csv")
                else: st.info("База данных пока пуста.")
            else: st.warning("Файл результатов еще не создан.")

# --- 9. ЭКРАН 2: ТЕСТ ---
elif st.session_state.test_state == "testing":
    elapsed = datetime.now() - st.session_state.start_time
    rem = timedelta(minutes=TEST_DURATION_MIN) - elapsed
    
    if rem.total_seconds() <= 0:
        st.session_state.test_state = "finishing"
        st.rerun()

    c1, c2 = st.columns([3, 1])
    c1.subheader(f"👤 {st.session_state.name}")
    c2.markdown(f"<div class='timer-box'>⏳ {max(0, int(rem.total_seconds()//60))}:{max(0, int(rem.total_seconds()%60)):02d}</div>", unsafe_allow_html=True)

    user_ans = []
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        st.markdown(f"**{i+1}. {q}**")
        a = st.radio(f"Вопрос {i}", opts, key=f"q_{i}", index=None, label_visibility="collapsed")
        user_ans.append(a)

    if st.button("ЗАВЕРШИТЬ РАБОТУ ✅"):
        if None in user_ans: st.warning("Вы ответили не на все вопросы!")
        else:
            st.session_state.user_ans = user_ans
            st.session_state.test_state = "finishing"
            st.rerun()

# --- 10. ЭКРАН 3: ИТОГИ ---
elif st.session_state.test_state == "finishing":
    score = 0
    total = len(st.session_state.questions)
    report = []
    
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        ua = st.session_state.user_ans[i] if i < len(st.session_state.user_ans) else "Нет ответа"
        is_corr = (ua == corr)
        if is_corr: score += 1
        report.append({"q": q, "ua": ua, "corr": corr, "status": "✅" if is_corr else "❌"})
    
    grade = get_grade(score, total)

    # ЗАЩИТА ОТ ДВОЙНОЙ ЗАПИСИ
    if not st.session_state.results_saved:
        save_result_to_file({
            "Дата": datetime.now().strftime("%d.%m %H:%M"),
            "ФИО": st.session_state.name,
            "Класс": st.session_state.u_class,
            "Баллы": f"{score}/{total}",
            "Оценка": grade
        })
        st.session_state.results_saved = True

    st.header(f"Ваш результат: {score} из {total}")
    st.subheader(f"Оценка: {grade}")
    
    st.write("### Разбор заданий:")
    for r in report:
        with st.expander(f"{r['status']} {r['q']}"):
            st.write(f"**Ваш ответ:** {r['ua']}")
            if r['status'] == "❌": 
                st.write(f"**Правильный ответ:** {r['corr']}")

    if st.button("ВЫЙТИ В НАЧАЛО"):
        st.session_state.test_state = "login"
        st.rerun()
