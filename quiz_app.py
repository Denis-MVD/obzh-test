import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import os
import plotly.express as px  # Для графиков (установится автоматически на Streamlit Cloud)

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="НВП: Система тестирования", layout="centered")

# --- 2. КОНСТАНТЫ И ФУНКЦИИ ---
TEACHER_PIN = "1234"
RESULTS_FILE = "detailed_results.csv"
TEST_DURATION_MIN = 15 # Время на тест в минутах

def save_result_to_file(data):
    file_exists = os.path.isfile(RESULTS_FILE)
    df = pd.DataFrame([data])
    df.to_csv(RESULTS_FILE, mode='a', index=False, header=not file_exists, encoding='utf-8-sig')

def get_grade(score, total):
    perc = (score / total) * 100
    if perc >= 90: return "5 (Отлично)"
    elif perc >= 70: return "4 (Хорошо)"
    elif perc >= 50: return "3 (Удовл.)"
    else: return "2 (Неуд.)"

# --- 3. ДИЗАЙН (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #e8e8e8; }
    div[data-testid="stVerticalBlock"] > div { 
        background-color: #3d4432 !important; 
        padding: 25px; border-radius: 10px; 
        border-left: 12px solid #2f3526 !important; margin-bottom: 20px;
    }
    h1, h2, h3, h4, p, label, .stMarkdown, .stRadio label {
        color: #ffffff !important; font-family: 'Segoe UI', sans-serif; 
        font-style: italic !important; font-weight: bold !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    .stApp h1, .stApp h2 { color: #2f3526 !important; font-style: normal !important; text-shadow: none; }
    input, select, div[data-baseweb="select"], div[data-baseweb="input"] {
        background-color: #2b2b2b !important; color: white !important; border: 1px solid white !important;
    }
    .stButton>button { 
        background-color: #2f3526 !important; color: white !important; 
        font-weight: bold; border: 2px solid white !important; width: 100%;
    }
    /* Стиль таймера */
    .timer-box { font-size: 24px; color: #ff4b4b; font-weight: bold; text-align: center; background: white; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. ВОПРОСЫ (10 и 11 классы) ---
# (Вопросы оставлены из вашего списка, 15 для 10 класса и 15 для 11)
questions_10 = [
    ("Что необходимо сделать в первую очередь при получении сигнала «Внимание всем!»?", ["Бежать на улицу", "Включить телевизор или радио", "Спрятаться в подвале", "Позвонить родственникам"], "Включить телевизор или радио"),
    ("Какое место в здании считается наиболее безопасным при землетрясении?", ["Возле окна", "В лифте", "Проем капитальных внутренних стен", "Угловая комната"], "Проем капитальных внутренних стен"),
    ("Если землетрясение застало вас на улице, где следует находиться?", ["Рядом с высоким зданием", "Под линией электропередач", "На открытой площадке вдали от зданий", "Внутри автомобиля"], "На открытой площадке вдали от зданий"),
    ("Что такое сель?", ["Снежная лавина", "Грязекаменный поток", "Подземный толчок", "Сильный ветер"], "Грязекаменный поток"),
    ("Ваши действия при угрозе схода селя?", ["Забраться на дерево", "Уйти в сторону, перпендикулярную направлению потока", "Побежать вниз по долине", "Остаться в доме"], "Уйти в сторону, перпендикулярную направлению потока"),
    ("Где лучше всего укрыться при внезапном урагане на открытой местности?", ["Под отдельно стоящим деревом", "В кювете или овраге", "За рекламным щитом", "На мосту"], "В кювете или овраге"),
    ("Какая дистанция от упавших проводов ЛЭП считается безопасной?", ["2 метра", "5 метров", "Не менее 8-10 метров", "1 метр"], "Не менее 8-10 метров"),
    ("Что входит в «тревожный чемодан» в первую очередь?", ["Документы, деньги, вода, аптечка", "Ноутбук и зарядка", "Запасная одежда и книги", "Посуда и инструменты"], "Документы, деньги, вода, аптечка"),
    ("Как следует передвигаться в зоне затопления при наводнении?", ["Вплавь", "Медленно, проверяя путь палкой", "Бегом", "Только на лодке"], "Медленно, проверяя путь палкой"),
    ("При лесном пожаре следует выходить:", ["По направлению ветра", "Против ветра, перпендикулярно кромке пожара", "Вглубь леса", "Оставаться на месте"], "Против ветра, перпендикулярно кромке пожара"),
    ("Основной поражающий фактор землетрясения?", ["Цунами", "Разрушение зданий и сооружений", "Град", "Гроза"], "Разрушение зданий и сооружений"),
    ("Что делать, если вы оказались в завале после землетрясения?", ["Постоянно кричать", "Экономить силы, подавать сигналы стуком", "Пытаться резко выбраться", "Поджечь спичку"], "Экономить силы, подавать сигналы стуком"),
    ("Первое действие при обнаружении возгорания в школе?", ["Продолжать урок", "Объявить эвакуацию и вызвать пожарных", "Начать тушить самостоятельно", "Открыть все окна"], "Объявить эвакуацию и вызвать пожарных"),
    ("При эвакуации во время пожара нужно:", ["Пользоваться лифтом", "Спускаться по лестнице", "Прыгать из окна", "Спрятаться под партой"], "Спускаться по лестнице"),
    ("Безопасное место в квартире при урагане?", ["Балкон", "Ванная комната или коридор", "Кухня", "Возле окна"], "Ванная комната или коридор")
]

questions_11 = [
    ("При аварии на АЭС с выбросом радиации, первым делом нужно:", ["Выйти на балкон", "Провести йодную профилактику и герметизировать помещение", "Уехать из города", "Открыть форточки"], "Провести йодную профилактику и герметизировать помещение"),
    ("Сигнал «Воздушная тревога» подается:", ["При угрозе наводнения", "При угрозе применения оружия противником", "При начале лесного пожара", "При землетрясении"], "При угрозе применения оружия противником"),
    ("Герметизация помещений при химической аварии включает:", ["Закрытие окон и заклеивание щелей", "Включение кондиционера", "Открытие вентиляции", "Разведение огня"], "Закрытие окон и заклеивание щелей"),
    ("При разливе ртути в помещении необходимо:", ["Смыть водой", "Собрать пылесосом", "Вызвать специалистов и проветрить", "Замести веником"], "Вызвать специалистов и проветрить"),
    ("Что делать при получении сообщения о террористической угрозе?", ["Игнорировать", "Сообщить в полицию, не трогать подозрительные предметы", "Самостоятельно осмотреть предмет", "Открыть предмет"], "Сообщить в полицию, не трогать подозрительные предметы"),
    ("К коллективным средствам защиты относятся:", ["Противогазы", "Убежища и укрытия", "Аптечки", "Респираторы"], "Убежища и укрытия"),
    ("Основная задача Гражданской обороны:", ["Проведение парадов", "Защита населения в военное время и при ЧС", "Строительство дорог", "Охрана границ"], "Защита населения в военное время и при ЧС"),
    ("При движении по зараженной местности следует:", ["Идти быстро, не поднимая пыли", "Бежать", "Ложиться на землю", "Собирать ягоды"], "Идти быстро, не поднимая пыли"),
    ("Индивидуальное средство защиты органов дыхания:", ["Плащ", "Ватно-марлевая повязка", "Перчатки", "Очки"], "Ватно-марлевая повязка"),
    ("Эвакуация населения — это:", ["Прогулка", "Организованный вывоз населения из опасных зон", "Бегство", "Переезд на дачу"], "Организованный вывоз населения из опасных зон"),
    ("При попадании капли АХОВ на кожу нужно:", ["Растереть", "Промыть большим количеством воды", "Заклеить пластырем", "Ничего не делать"], "Промыть большим количеством воды"),
    ("Что делать при угрозе обрушения здания?", ["Искать ценные вещи", "Покинуть здание по лестнице", "Зайти в лифт", "Выйти на балкон"], "Покинуть здание по лестнице"),
    ("Признак радиационной опасности:", ["Запах чеснока", "Специфический звук", "Отсутствует (обнаруживается приборами)", "Яркий свет"], "Отсутствует (обнаруживается приборами)"),
    ("К поражающим факторам ядерного взрыва не относится:", ["Ударная волна", "Световое излучение", "Селевой поток", "Проникающая радиация"], "Селевой поток"),
    ("Для защиты от аммиака повязку смачивают:", ["Раствором соды", "Раствором лимонной кислоты", "Спиртом", "Маслом"], "Раствором лимонной кислоты")
]

# --- 5. ИНИЦИАЛИЗАЦИЯ ---
if 'test_state' not in st.session_state: st.session_state.test_state = "login"

# --- 6. ЭКРАН 1: ВХОД ---
if st.session_state.test_state == "login":
    st.title("🎖️ ЗАЧЕТ ПО НВП / ОБЖ")
    name = st.text_input("Фамилия и Имя:")
    u_class = st.selectbox("Класс:", ["10 класс", "11 класс"])
    
    if st.button("НАЧАТЬ ТЕСТ 🚀"):
        if name:
            st.session_state.name = name
            st.session_state.u_class = u_class
            st.session_state.start_time = datetime.now()
            # Выбор и перемешивание вопросов + перемешивание ответов
            raw_q = questions_10 if u_class == "10 класс" else questions_11
            shuffled = []
            for q_text, opts, corr in random.sample(raw_q, len(raw_q)):
                sh_opts = random.sample(opts, len(opts)) # Перемешиваем варианты
                shuffled.append((q_text, sh_opts, corr))
            st.session_state.questions = shuffled
            st.session_state.test_state = "testing"
            st.rerun()

    st.divider()
    with st.expander("📊 КАБИНЕТ ПРЕПОДАВАТЕЛЯ"):
        pin = st.text_input("ПИН:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                df = pd.read_csv(RESULTS_FILE)
                st.write("### Успеваемость")
                # График
                if not df.empty:
                    fig = px.pie(df, names='Оценка', title='Распределение оценок в классе', hole=0.3)
                    st.plotly_chart(fig)
                st.dataframe(df[["Дата", "ФИО", "Класс", "Баллы", "Оценка"]])
                st.download_button("📥 СКАЧАТЬ ВЕДОМОСТЬ", df.to_csv(index=False).encode('utf-8-sig'), "results.csv")

# --- 7. ЭКРАН 2: ТЕСТ С ТАЙМЕРОМ ---
elif st.session_state.test_state == "testing":
    # Расчет времени
    elapsed = datetime.now() - st.session_state.start_time
    remaining = timedelta(minutes=TEST_DURATION_MIN) - elapsed
    
    if remaining.total_seconds() <= 0:
        st.session_state.test_state = "finishing"
        st.rerun()

    cols = st.columns([3, 1])
    cols[0].subheader(f"👤 {st.session_state.name} ({st.session_state.u_class})")
    cols[1].markdown(f"<div class='timer-box'>⏳ {int(remaining.total_seconds()//60)}:{int(remaining.total_seconds()%60):02d}</div>", unsafe_allow_html=True)

    u_answers = []
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        st.markdown(f"**{i+1}. {q}**")
        ans = st.radio(f"Ответ на вопрос {i+1}:", opts, key=f"q{i}", index=None, label_visibility="collapsed")
        u_answers.append(ans)

    if st.button("РАПОРТ СДАТЬ ✅"):
        if None in u_answers: st.warning("Ответьте на все вопросы!")
        else:
            st.session_state.u_answers = u_answers
            st.session_state.test_state = "finishing"
            st.rerun()
    
    st.empty() # Для автообновления таймера (в Streamlit Cloud работает по взаимодействию)

# --- 8. ЭКРАН 3: ИТОГИ И РАЗБОР ---
elif st.session_state.test_state == "finishing":
    score = 0
    details = []
    total = len(st.session_state.questions)
    
    for i, (q, opts, corr) in enumerate(st.session_state.questions):
        user_ans = st.session_state.u_answers[i] if i < len(st.session_state.u_answers) else "Нет ответа"
        if user_ans == corr:
            score += 1
            details.append({"Вопрос": q, "Ваш ответ": user_ans, "Статус": "✅ Верно", "Правильный": corr})
        else:
            details.append({"Вопрос": q, "Ваш ответ": user_ans, "Статус": "❌ Ошибка", "Правильный": corr})
    
    grade = get_grade(score, total)
    
    st.header(f"РЕЗУЛЬТАТ: {score} из {total}")
    st.subheader(f"ВАША ОЦЕНКА: {grade}")

    # Сохранение
    save_result_to_file({
        "Дата": datetime.now().strftime("%d.%m %H:%M"),
        "ФИО": st.session_state.name,
        "Класс": st.session_state.u_class,
        "Баллы": f"{score}/{total}",
        "Оценка": grade
    })

    st.write("### 📝 ПОЛНЫЙ РАЗБОР ВОПРОСОВ:")
    for item in details:
        with st.expander(f"{item['Статус']} | {item['Вопрос']}"):
            st.write(f"**Ваш ответ:** {item['Ваш ответ']}")
            if "❌" in item['Статус']:
                st.write(f"**Правильный ответ:** {item['Правильный']}")

    if st.button("ВЫЙТИ"):
        st.session_state.test_state = "login"
        st.rerun()
