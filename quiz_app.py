import streamlit as st
import random
from datetime import datetime, timedelta
import pandas as pd
import os
import base64
from streamlit_autorefresh import st_autorefresh

# --- ИНТЕРФЕЙС И СТИЛИ ---
def get_base64(bin_file):
    if os.path.exists(bin_file):
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

def set_design(bg_file):
    bin_str = get_base64(bg_file)
    bg_img = f'url("data:image/png;base64,{bin_str}")' if bin_str else "linear-gradient(to bottom, #1a2a1a, #000000)"
    
    st.markdown(f'''
    <style>
    .stApp {{
        background-image: {bg_img};
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .sticky-timer {{
        position: fixed;
        top: 0; left: 0; width: 100%;
        background: rgba(180, 40, 40, 0.95);
        color: white; text-align: center;
        padding: 12px; z-index: 1000;
        font-weight: bold; font-size: 1.2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.6);
    }}
    #MainMenu, footer, header {{visibility: hidden;}}
    div[data-testid="stVerticalBlock"] > div:has(h1, h2, h3, h4, .stTextInput, .stButton, .stExpander, p, span) {{
        background-color: rgba(50, 60, 45, 0.92) !important;
        padding: 20px; border-radius: 15px;
        border-left: 10px solid #2f3526 !important;
        margin-bottom: 20px; color: white;
    }}
    .stRadio > label {{ color: #ffffff !important; font-size: 1.1rem; font-weight: bold; }}
    </style>
    ''', unsafe_allow_html=True)

# --- НАСТРОЙКИ ---
st.set_page_config(page_title="НВП Контроль", layout="centered", page_icon="🎖️")
set_design('background.png')

RESULTS_FILE = "results_nvp.csv"
TEACHER_PIN = "1234"
TEST_TIME = 20

# --- ПОЛНАЯ БАЗА ДАННЫХ (ВСЕ 7 ТЕМ) ---
DATABASE = {
    "10 класс": {
        "Тема 1: Действия в районах стихийных бедствий": [
            ("Что нужно сделать первым при сигнале «Внимание всем!»?", ["Бежать на улицу", "Включить ТВ или радио", "Позвонить соседям", "Закрыть окна"], "Включить ТВ или радио"),
            ("Безопасное место в здании при землетрясении?", ["Лифт", "У окна", "Проем капитальных стен", "Угловая комната"], "Проем капитальных стен"),
            ("Где лучше находиться на улице во время землетрясения?", ["Под ЛЭП", "На открытой площадке", "У высокого здания", "В подземном переходе"], "На открытой площадке"),
            ("Что такое сель?", ["Снежная лавина", "Грязекаменный поток", "Сильный ветер", "Наводнение"], "Грязекаменный поток"),
            ("Действия при угрозе селя?", ["Бежать вниз по долине", "Подняться на дерево", "Уйти в сторону, перпендикулярно потоку", "Остаться в доме"], "Уйти в сторону, перпендикулярно потоку"),
            ("Укрытие при урагане в открытом поле?", ["Под отдельно стоящим деревом", "В кювете или овраге", "За легким забором", "Стоять в полный рост"], "В кювете или овраге"),
            ("Безопасная дистанция от оборванного провода ЛЭП?", ["1 метр", "3 метра", "8-10 метров", "15 метров"], "8-10 метров"),
            ("Что входит в «тревожный чемодан» в первую очередь?", ["Ноутбук", "Документы, вода, аптечка", "Одежда", "Посуда"], "Документы, вода, аптечка"),
            ("Выход из зоны лесного пожара:", ["По ветру", "Вглубь леса", "Против ветра, перпендикулярно кромке", "На месте"], "Против ветра, перпендикулярно кромке"),
            ("Лучшее место в квартире при урагане?", ["Балкон", "Ванная/Коридор", "Кухня", "Окно"], "Ванная/Коридор")
        ],
        "Тема 2: ПМП при ранениях, кровотечениях и ожогах": [
            ("Признак артериального кровотечения:", ["Кровь темная", "Кровь алая, пульсирующая струя", "Кровь сочится", "Синяк"], "Кровь алая, пульсирующая струя"),
            ("Куда накладывается жгут при артериальном кровотечении?", ["Ниже раны", "Выше раны", "На рану", "На туловище"], "Выше раны"),
            ("Максимальное время наложения жгута летом?", ["30 минут", "1 час", "2 часа", "5 часов"], "1 час"),
            ("Что нужно сделать при венозном кровотечении?", ["Наложить жгут", "Давящая повязка", "Прижечь йодом", "Ничего"], "Давящая повязка"),
            ("Первая помощь при термическом ожоге 1-2 степени?", ["Смазать маслом", "Охладить проточной водой", "Проколоть пузыри", "Посыпать солью"], "Охладить проточной водой"),
            ("Как обрабатывают края раны йодом?", ["Заливают внутрь", "Смазывают кожу вокруг раны", "Протирают дно", "Не используют"], "Смазывают кожу вокруг раны"),
            ("Признак венозного кровотечения:", ["Алая кровь", "Темно-вишневая кровь, течет равномерно", "Кровь пенится", "Пульсация"], "Темно-вишневая кровь, течет равномерно"),
            ("Помощь при носовом кровотечении:", ["Запрокинуть голову", "Наклонить вперед, холод на переносицу", "Лечь на спину", "Сморкаться"], "Наклонить вперед, холод на переносицу"),
            ("Основная цель наложения повязки?", ["Защита раны и остановка крови", "Для красоты", "Не видеть рану", "Замена лекарства"], "Защита раны и остановка крови"),
            ("Что нельзя делать с инородным телом в ране?", ["Оставлять", "Извлекать самостоятельно", "Фиксировать", "Промывать вокруг"], "Извлекать самостоятельно")
        ],
        "Тема 3: ПМП при различных несчастных случаях": [
            ("Соотношение нажатий и вдохов при СЛР?", ["15:2", "30:2", "10:1", "5:2"], "30:2"),
            ("Где проверяют пульс у пострадавшего без сознания?", ["На запястье", "На сонной артерии", "На виске", "На животе"], "На сонной артерии"),
            ("Помощь при обморожении:", ["Растереть снегом", "Постепенное согревание, теплое питье", "Растереть спиртом", "Горячая ванна"], "Постепенное согревание, теплое питье"),
            ("Признак клинической смерти:", ["Нет дыхания и пульса на сонной артерии", "Сонливость", "Боль", "Головокружение"], "Нет дыхания и пульса на сонной артерии"),
            ("Глубина нажатия на грудную клетку при СЛР?", ["1-2 см", "5-6 см", "10 см", "Не прогибать"], "5-6 см"),
            ("Транспортировка без сознания:", ["На спине", "На животе", "Устойчивое боковое положение", "Сидя"], "Устойчивое боковое положение")
        ],
        "Тема 4: Строи и их элементы. Строевая стойка": [
            ("Шеренга — это строй, в котором военнослужащие размещены:", ["В затылок", "Один возле другого по фронту", "В две линии", "Случайно"], "Один возле другого по фронту"),
            ("Колонна — это строй, в котором военнослужащие расположены:", ["По фронту", "В затылок друг другу", "По кругу", "Буквой П"], "В затылок друг другу"),
            ("Дистанция — это расстояние:", ["По фронту", "В глубину между военнослужащими", "Между частями", "До цели"], "В глубину между военнослужащими"),
            ("Интервал — это расстояние:", ["По фронту между военнослужащими", "В глубину", "Между полками", "От штаба"], "По фронту между военнослужащими"),
            ("По команде «ВОЛЬНО» разрешается:", ["Уходить", "Ослабить одну ногу в колене", "Курить", "Смеяться"], "Ослабить одну ногу в колене")
        ],
        "Тема 5: Повороты на месте. Строевой шаг": [
            ("Поворот кругом выполняется через:", ["Правое плечо", "Левое плечо", "Любое", "Через голову"], "Левое плечо"),
            ("Темп строевого шага (шагов в минуту):", ["80-90", "110-120", "140-150", "60-70"], "110-120"),
            ("Высота подъема ноги при строевом шаге?", ["5-10 см", "15-20 см", "30-40 см", "0 см"], "15-20 см"),
            ("Команда «Стой» подается под:", ["Левую ногу", "Правую ногу", "Любую", "Обе"], "Правую ногу")
        ],
        "Тема 6: Ориентирование на местности без карты": [
            ("С какой стороны дерева растет мох?", ["Юг", "Север", "Запад", "Восток"], "Север"),
            ("Где быстрее тает снег весной на склонах?", ["Северные", "Южные", "Везде", "На дне"], "Южные"),
            ("Муравейники расположены с какой стороны дерева?", ["Северной", "Южной", "Западной", "Восточной"], "Южной"),
            ("Полярная звезда всегда на:", ["Юге", "Севере", "Зените", "Востоке"], "Севере"),
            ("В полдень тень указывает на:", ["Юг", "Север", "Запад", "Восток"], "Север"),
            ("Кольца на пнях шире с:", ["Северной", "Южной", "Западной", "Восточной"], "Южной"),
            ("Прибор для определения сторон горизонта:", ["Барометр", "Компас", "Термометр", "Часы"], "Компас"),
            ("Если встать лицом к северу, за спиной будет:", ["Восток", "Юг", "Запад", "Право"], "Юг")
        ],
        "Тема 7: Определение магнитного азимута": [
            ("Что такое азимут?", ["Расстояние", "Угол между севером и объектом", "Высота", "Маршрут"], "Угол между севером и объектом"),
            ("Азимут направления на Восток?", ["0°", "90°", "180°", "270°"], "90°"),
            ("Азимут направления на Юг?", ["90°", "180°", "270°", "360°"], "180°"),
            ("Азимут направления на Запад?", ["90°", "180°", "270°", "0°"], "270°"),
            ("Азимут измеряется:", ["Против часовой", "По часовой стрелке", "От объекта", "С запада"], "По часовой стрелке"),
            ("Обратный азимут — это:", ["Задний", "Направление, противоположное прямому", "Минус", "Ложный"], "Направление, противоположное прямому"),
            ("Прямой азимут 300°, обратный равен:", ["480°", "120°", "150°", "30°"], "120°"),
            ("Мушка компаса направляется на:", ["Север", "Объект (цель)", "Землю", "Солнце"], "Объект (цель)")
        ]
    },
    "11 класс": { "Раздел в разработке": [("Вопрос", ["Ответ"], "Ответ")] }
}

# --- ЛОГИКА ПРИЛОЖЕНИЯ ---
if 'state' not in st.session_state: st.session_state.state = "login"
if 'ans' not in st.session_state: st.session_state.ans = {}

# --- ЭКРАН ВХОДА ---
if st.session_state.state == "login":
    st.markdown("<h3 style='text-align: center; color: white;'>🎖️ СИСТЕМА КОНТРОЛЯ ЗНАНИЙ НВП</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #ccc;'>Преподаватель: Семенков Денис Алексеевич</p>", unsafe_allow_html=True)
    
    name = st.text_input("Фамилия и Имя ученика:")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("10 КЛАСС 📘", use_container_width=True): st.session_state.sel_class = "10 класс"
    with col2:
        if st.button("11 КЛАСС 📕", use_container_width=True): st.session_state.sel_class = "11 класс"

    if 'sel_class' in st.session_state:
        st.info(f"Выбран: {st.session_state.sel_class}")
        themes = DATABASE[st.session_state.sel_class]
        for t_name in themes.keys():
            if st.button(t_name, use_container_width=True):
                if name:
                    st.session_state.u_name = name
                    st.session_state.u_class = st.session_state.sel_class
                    st.session_state.u_theme = t_name
                    st.session_state.start_time = datetime.now()
                    st.session_state.ans = {}
                    
                    # Перемешивание вопросов
                    raw_qs = themes[t_name]
                    shuffled = []
                    for q, opts, corr in random.sample(raw_qs, len(raw_qs)):
                        shuffled.append((q, random.sample(opts, len(opts)), corr))
                    
                    st.session_state.qs = shuffled
                    st.session_state.state = "test"
                    st.rerun()
                else:
                    st.error("⚠️ Пожалуйста, введите Фамилию и Имя!")

    with st.expander("📊 КАБИНЕТ ПРЕПОДАВАТЕЛЯ"):
        pin = st.text_input("Введите PIN:", type="password")
        if pin == TEACHER_PIN:
            if os.path.exists(RESULTS_FILE):
                st.dataframe(pd.read_csv(RESULTS_FILE), use_container_width=True)

# --- ЭКРАН ТЕСТА ---
elif st.session_state.state == "test":
    st_autorefresh(interval=1000, key="timer_refresh")
    
    elapsed = datetime.now() - st.session_state.start_time
    rem = timedelta(minutes=TEST_TIME) - elapsed
    sec = max(0, int(rem.total_seconds()))
    mm, ss = divmod(sec, 60)
    
    st.markdown(f'<div class="sticky-timer">⏱️ ОСТАТОК ВРЕМЕНИ: {mm:02d}:{ss:02d}</div>', unsafe_allow_html=True)
    st.write("###")

    if sec <= 0:
        st.session_state.state = "fin"; st.rerun()

    st.markdown(f"👤 **Ученик:** {st.session_state.u_name} | 🚩 **Тема:** {st.session_state.u_theme}")
    
    for i, (q, opts, corr) in enumerate(st.session_state.qs):
        st.markdown(f"**{i+1}. {q}**")
        st.session_state.ans[i] = st.radio(
            f"label_{i}", opts, 
            index=opts.index(st.session_state.ans[i]) if i in st.session_state.ans else None,
            key=f"radio_{i}", label_visibility="collapsed"
        )

    if st.button("ЗАВЕРШИТЬ ТЕСТ ✅", use_container_width=True):
        if len(st.session_state.ans) < len(st.session_state.qs):
            st.warning("Ответьте на все вопросы перед завершением!")
        else:
            st.session_state.state = "fin"; st.rerun()

# --- ЭКРАН РЕЗУЛЬТАТОВ ---
elif st.session_state.state == "fin":
    score = sum(1 for i, (q, o, c) in enumerate(st.session_state.qs) if st.session_state.ans.get(i) == c)
    total = len(st.session_state.qs)
    perc = (score/total)*100
    grade = "5 (Отлично)" if perc>=90 else "4 (Хорошо)" if perc>=75 else "3 (Удовл.)" if perc>=50 else "2 (Неуд.)"
    
    if 'saved' not in st.session_state:
        df = pd.DataFrame([{
            "Дата": datetime.now().strftime("%d.%m %H:%M"),
            "Имя": st.session_state.u_name,
            "Класс": st.session_state.u_class,
            "Тема": st.session_state.u_theme,
            "Баллы": f"{score}/{total}",
            "Оценка": grade
        }])
        df.to_csv(RESULTS_FILE, mode='a', index=False, header=not os.path.exists(RESULTS_FILE), encoding='utf-8-sig')
        st.session_state.saved = True

    st.markdown(f"<h1 style='text-align: center;'>Ваш результат: {score} из {total}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align: center; color: gold;'>Оценка: {grade}</h2>", unsafe_allow_html=True)

    with st.expander("🔍 ПОСМОТРЕТЬ РАБОТУ НАД ОШИБКАМИ"):
        for i, (q, o, c) in enumerate(st.session_state.qs):
            u_ans = st.session_state.ans.get(i)
            is_correct = (u_ans == c)
            bg = "rgba(40, 167, 69, 0.2)" if is_correct else "rgba(220, 53, 69, 0.2)"
            border = "#28a745" if is_correct else "#dc3545"
            
            st.markdown(f"""
            <div style="background:{bg}; border: 1px solid {border}; padding: 15px; border-radius: 10px; margin-bottom: 10px; color: white;">
                <strong>Вопрос {i+1}: {q}</strong><br>
                Ваш ответ: <i>{u_ans}</i><br>
                {"✅ Верно!" if is_correct else f"❌ Ошибка. Правильный ответ: <b>{c}</b>"}
            </div>
            """, unsafe_allow_html=True)

    if st.button("ВЕРНУТЬСЯ В ГЛАВНОЕ МЕНЮ"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.rerun()
