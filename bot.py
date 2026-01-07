import asyncio
import logging
import os
import random
from collections import Counter

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.client.default import DefaultBotProperties

# =========================
# TOKEN (скрытый, из терминала)
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError('❌ BOT_TOKEN не найден. Запусти: export BOT_TOKEN="твой_токен"')

logging.basicConfig(level=logging.INFO)

# aiogram 3.24.0 — parse_mode только через DefaultBotProperties
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# =========================
# ТЕКСТЫ
# =========================
WELCOME_TEXT = (
    "Привет, звездочка! 🌟 Рады что ты тут! Давай знакомиться! Я профориентационный Бот Умскул! "
    "И я тебе буду помогать с выбором профессии мечты!\n\n"
    "Ты сейчас делаешь большой шаг, чтобы узнать себя поближе и найти свою профессию мечты!!))\n\n"
    "С чего хочешь начать?🥰"
)

PROFKOD_INTRO_TEXT = (
    "<b>ПрофКод - отличный выбор, если хочешь понять, взломать код Типа профессий, что тебе подходит!😉</b>\n\n"
    "Давай пройдем его вместе!🫶\n\n"
    "<b>Что нужно будет делать?🤔</b>\n\n"
    "В этом тесте тебе будет предложено сыграть в 2 раунда!\n"
    "В каждом раунде нужно выбрать одну из двух профессий!⚡️⚡️⚡️\n\n"
    "Это не значит, что только эти профессии ты сможешь реализовать в карьере мечты. "
    "Этот тест поможет по примерам профессий определить тип профессий, который тебе может быть интереснее и ближе.🥰\n\n"
    "А если для тебя профессия будет не знакома из списка, ты можешь нажать кнопку <b>«Подробнее»</b> "
    "и узнать больше о её функциях))🔥\n\n"
    "💡Подсказка: если тебе нравятся обе профессии или совсем не нравятся обе профессии из пары — "
    "постарайся выбрать ту что ближе из двух"
)

ROUND2_PROMPT_TEXT = "Готов(а) ко второму раунду, чтобы узнать свой тип профессии?"
FINAL_PROMPT_TEXT = "Так волнительно!😱🥰 Подведем итоги теста?"

FINAL_INTRO_TEXT = (
    "Ваууу! 😱Поздравляю тебя, звездочка! 🤩\n\n"
    "Это твои топ 3 типа профессий, по которым ты сможешь найти те профессии, что будут тебе ближе и интереснее!  "
    "Приоритете тот тип, который набрал больше всего твоих голосов☺️☺️☺️\n\n"
    "🤫🫣😍Но раскрою тебе секрет: есть профессии, что могут совмещать в себе сразу 2-3 типа! 😱\n"
    "Именно поэтому мы не выбираем один тип! Чем шире кругозор, тем ответственнее мы подойдем к выбору той самой профессии мечты! "
    "Переходи по ссылкам к типам профессий и изучи, какие профессии есть в нашем архиве! Может та самая - ждет тебя уже сейчас!😉😍\n\n"
)

# =========================
# КНОПКИ (убрали "О тесте", добавили "Старт")
# =========================
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎯 Тест ПрофКод")],
        [KeyboardButton(text="🔄 Старт")],
    ],
    resize_keyboard=True,
)

# =========================
# ДАННЫЕ
# =========================
PROF_NAMES = {
    1: "🥗 Нутрициолог", 2: "⭐ Астрофизик", 3: "🐾 Зоолог", 4: "💊 Валеолог", 5: "🪨 Геолог",
    6: "🧠 Психолог", 7: "📈 Коуч", 8: "⚖️ Конфликтолог", 9: "💼 Бизнес-тренер", 10: "🎲 Игропедагог",
    11: "🏢 GR-менеджер", 12: "👥 Комьюнити-менеджер", 13: "🔍 Хэдхантер", 14: "⚖️ Сетевой юрист", 15: "📣 Пиар-менеджер",
    16: "🔗 SEO-оптимизатор", 17: "📊 Аналитик Big Data", 18: "💻 Web-программист", 19: "📈 Актуарий", 20: "💰 Инвестиционный аналитик",
    21: "🎬 Художник-мультипликатор", 22: "🎥 Кинокритик", 23: "✨ Мэппинг-режиссер", 24: "👗 Стилист-шопер", 25: "🖼️ Арт-оценщик",
    26: "🍰 Пастижер", 27: "👨‍🍳 Повар", 28: "💎 Ювелир", 29: "💉 Мастер татуажа", 30: "🧵 Портной",
    31: "✍️ Сценарист", 32: "📝 Копирайтер", 33: "🗣️ Спитчрайтер", 34: "📻 Диктор Радио и ТВ", 35: "🌐 Переводчик",
    36: "💪 Фитнес-тренер", 37: "👮 Полицейский", 38: "🏅 Профессиональный спортсмен", 39: "🚒 Спасатель МЧС", 40: "🥾 Инструктор по туризму",
    41: "📋 Менеджер проекта", 42: "📈 Директор по развитию", 43: "🚀 Ментор стартапов", 44: "🎤 Продюсер", 45: "🏛️ Политик",
    46: "🔬 Электрохимик", 47: "🍲 Технолог пищевого производства", 48: "🏗️ Архитектор", 49: "🔧 Инженер конструктор", 50: "🖨️ Инженер 3D печати",
}

# Коротко и максимально понятно (без путаницы) — кнопки A/B + короткое имя
PROF_SHORT = {
    1: "Нутрициолог", 2: "Астрофизик", 3: "Зоолог", 4: "Валеолог", 5: "Геолог",
    6: "Психолог", 7: "Коуч", 8: "Конфликтолог", 9: "Бизнес-тренер", 10: "Игропедагог",
    11: "GR-менеджер", 12: "Комьюнити", 13: "Хэдхантер", 14: "Сетевой юрист", 15: "Пиар-менеджер",
    16: "SEO", 17: "Big Data", 18: "Web-прог", 19: "Актуарий", 20: "Инвест-аналит",
    21: "Мультик", 22: "Кинокритик", 23: "Мэппинг", 24: "Стилист", 25: "Арт-оценщик",
    26: "Пастижер", 27: "Повар", 28: "Ювелир", 29: "Татуаж", 30: "Портной",
    31: "Сценарист", 32: "Копирайтер", 33: "Спитчрайтер", 34: "Диктор", 35: "Переводчик",
    36: "Фитнес", 37: "Полиция", 38: "Спортсмен", 39: "МЧС", 40: "Туризм",
    41: "Менеджер пр.", 42: "Директор разв.", 43: "Ментор", 44: "Продюсер", 45: "Политик",
    46: "Электрохимик", 47: "Технолог", 48: "Архитектор", 49: "Инженер", 50: "3D-инженер",
}

PROF_DESCRIPTIONS = {
    1: "Специалист по связи питания и здоровья человека",
    2: "Изучает небесные тела и процессы во Вселенной",
    3: "Изучает животных и их поведение",
    4: "Занимается сохранением и укреплением здоровья",
    5: "Исследует горные породы и полезные ископаемые",
    6: "Помогает решать психологические трудности",
    7: "Помогает раскрывать потенциал и эффективность",
    8: "Предотвращает и разрешает конфликты",
    9: "Обучает и развивает персонал",
    10: "Создает обучение через игровые методики",
    11: "Взаимодействует с госструктурами (GR)",
    12: "Развивает сообщества и коммуникацию",
    13: "Ищет специалистов на ключевые роли",
    14: "Право и нормы в цифровой среде и интернете",
    15: "Управляет PR и имиджем",
    16: "Продвигает сайты в поисковых системах",
    17: "Анализирует большие массивы данных",
    18: "Создает сайты и web-сервисы",
    19: "Оценивает финансовые/страховые риски",
    20: "Оценивает инвестиции и рынки",
    21: "Создает мультфильмы и анимацию",
    22: "Анализирует фильмы и пишет рецензии",
    23: "Создает 3D-проекции и шоу",
    24: "Подбирает стиль и гардероб",
    25: "Оценивает произведения искусства",
    26: "Изготавливает изделия из натуральных волос",
    27: "Готовит блюда и управляет кухней",
    28: "Создает украшения",
    29: "Делает перманентный макияж",
    30: "Шьет изделия по заказу",
    31: "Пишет основу сценария",
    32: "Пишет рекламные тексты",
    33: "Пишет тексты выступлений",
    34: "Озвучивает и ведет эфир",
    35: "Переводит устно и письменно",
    36: "Ведет тренировки",
    37: "Обеспечивает правопорядок",
    38: "Профессионально занимается спортом",
    39: "Спасает людей в ЧС",
    40: "Обучает туризму и маршрутам",
    41: "Управляет проектом",
    42: "Развивает бизнес и рост",
    43: "Наставляет стартапы",
    44: "Руководит медиа-проектами",
    45: "Публичная политика",
    46: "Электрохимические процессы",
    47: "Контроль пищевого производства",
    48: "Проектирует здания",
    49: "Проектирует конструкции",
    50: "Внедряет 3D-печать",
}

COLORS = {
    1: "зеленый", 2: "зеленый", 3: "зеленый", 4: "зеленый", 5: "зеленый",
    6: "лиловый", 7: "лиловый", 8: "лиловый", 9: "лиловый", 10: "лиловый",
    11: "светло рыжий", 12: "светло рыжий", 13: "светло рыжий", 14: "светло рыжий", 15: "светло рыжий",
    16: "голубой", 17: "голубой", 18: "голубой", 19: "голубой", 20: "голубой",
    21: "желтый", 22: "желтый", 23: "желтый", 24: "желтый", 25: "желтый",
    26: "серый", 27: "серый", 28: "серый", 29: "серый", 30: "серый",
    31: "изумрудный", 32: "изумрудный", 33: "изумрудный", 34: "изумрудный", 35: "изумрудный",
    36: "ярко оранжевый", 37: "ярко оранжевый", 38: "ярко оранжевый", 39: "ярко оранжевый", 40: "ярко оранжевый",
    41: "ярко розовый", 42: "ярко розовый", 43: "ярко розовый", 44: "ярко розовый", 45: "ярко розовый",
    46: "белый", 47: "белый", 48: "белый", 49: "белый", 50: "белый",
}

TYPE_DESCRIPTIONS = {
    "зеленый": {"emoji": "🌿", "name": "Натуралистический", "desc": "Любят природу, животных и растения. Предметы: биология, география, химия, физика.", "link": "https://profkrisglad.tilda.ws/page22904672.html"},
    "лиловый": {"emoji": "🤔", "name": "Внутриличностный", "desc": "Эмпатия, рефлексия, осознанность, поддержка и развитие.", "link": "https://profkrisglad.tilda.ws/page22909916.html"},
    "светло рыжий": {"emoji": "🤝", "name": "Межличностный", "desc": "Коммуникации, переговоры, контакт с людьми, презентации.", "link": "https://profkrisglad.tilda.ws/page22905673.html"},
    "голубой": {"emoji": "💻", "name": "Цифровой", "desc": "Логика, аналитика, цифры, данные, код.", "link": "https://profkrisglad.tilda.ws/page22908598.html"},
    "желтый": {"emoji": "🎨", "name": "Художественный", "desc": "Творчество, стиль, воображение, эстетика.", "link": "https://profkrisglad.tilda.ws/page22899555.html"},
    "серый": {"emoji": "🔧", "name": "Прикладной", "desc": "Ручной труд, инструменты, создание вещей своими руками.", "link": "https://profkrisglad.tilda.ws/page22909449.html"},
    "изумрудный": {"emoji": "📝", "name": "Вербально-лингвистический", "desc": "Речь, тексты, языки, выступления.", "link": "https://profkrisglad.tilda.ws/page22880053.html"},
    "ярко оранжевый": {"emoji": "⚡", "name": "Физический", "desc": "Сила, выносливость, спорт, практика.", "link": "https://profkrisglad.tilda.ws/page22902370.html"},
    "ярко розовый": {"emoji": "👑", "name": "Лидерский", "desc": "Управление, решения, ответственность, переговоры.", "link": "https://profkrisglad.tilda.ws/page22902902.html"},
    "белый": {"emoji": "🔬", "name": "Технико-технологический", "desc": "Инженерия, техника, схемы, математика.", "link": "https://profkrisglad.tilda.ws/page22898516.html"},
}

# =========================
# Состояние пользователей
# =========================
current_users = {}

def reset_user(user_id: int):
    current_users[user_id] = {
        "round": 1,
        "pair": 0,
        "round1_winners": [],
        "round2_winners": [],
        "used_in_round2": [],
    }

def pick_pair_round2(finalists, used):
    available = [p for p in finalists if p not in used]
    if len(available) < 2:
        return None, None

    # стараемся выбирать разный цвет
    for _ in range(300):
        p1 = random.choice(available)
        candidates = [p for p in available if p != p1 and COLORS[p] != COLORS[p1]]
        if candidates:
            return p1, random.choice(candidates)

    # если не получилось — любые
    return available[0], available[1]

# =========================
# /start и "Старт"
# =========================
@dp.message(CommandStart())
async def start_cmd(message: Message):
    current_users.pop(message.from_user.id, None)
    await message.answer(WELCOME_TEXT, reply_markup=MAIN_KEYBOARD)

@dp.message(lambda m: m.text and "старт" == m.text.strip().lower().replace("🔄", "").strip())
async def restart_cmd(message: Message):
    current_users.pop(message.from_user.id, None)
    await message.answer(WELCOME_TEXT, reply_markup=MAIN_KEYBOARD)

# =========================
# ВАЖНО: ловим "ПрофКод" по слову (а не строго по кнопке)
# =========================
@dp.message(lambda m: m.text and "профкод" in m.text.lower())
async def profkod_intro(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Стартуем?", callback_data="start_prof_test")]
    ])
    await message.answer(PROFKOD_INTRO_TEXT, reply_markup=kb)

@dp.callback_query(F.data == "start_prof_test")
async def start_prof_test_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    reset_user(user_id)
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(callback.message.chat.id, "🚀 <b>Тест начался!</b>")
    await show_pair(callback.message.chat.id, user_id)

# =========================
# Показ пары
# =========================
async def show_pair(chat_id, user_id):
    user_data = current_users.get(user_id)
    if not user_data:
        return

    # РАУНД 1: 1..25 VS 26..50
    if user_data["round"] == 1:
        pair_num = user_data["pair"]
        if pair_num >= 25:
            user_data["round"] = 2
            user_data["pair"] = 0
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Гоу!", callback_data="go_round2")]
            ])
            await bot.send_message(chat_id, f"<b>{ROUND2_PROMPT_TEXT}</b>", reply_markup=kb)
            return

        prof1 = pair_num + 1
        prof2 = pair_num + 26
        header = f"🥊 <b>РАУНД 1</b> • ПАРА {pair_num + 1}/25"

    # РАУНД 2: 12 пар финалистов
    else:
        pair_num = user_data["pair"]
        if pair_num >= 12:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Итоги теста ПрофКод", callback_data="show_final")]
            ])
            await bot.send_message(chat_id, f"<b>{FINAL_PROMPT_TEXT}</b>", reply_markup=kb)
            return

        finalists = user_data["round1_winners"]
        prof1, prof2 = pick_pair_round2(finalists, user_data["used_in_round2"])
        if not prof1 or not prof2:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Итоги теста ПрофКод", callback_data="show_final")]
            ])
            await bot.send_message(chat_id, f"<b>{FINAL_PROMPT_TEXT}</b>", reply_markup=kb)
            return

        user_data["used_in_round2"].extend([prof1, prof2])
        header = f"🔥 <b>РАУНД 2</b> • ПАРА {pair_num + 1}/12"

    # Текст пары: названия жирным + описание
    text = (
        f"{header}\n\n"
        f"🅰️ <b>{PROF_NAMES[prof1]}</b>\n"
        f"<i>{PROF_DESCRIPTIONS.get(prof1, '')}</i>\n\n"
        f"⚔️ <b>ПРОТИВ</b> ⚔️\n\n"
        f"🅱️ <b>{PROF_NAMES[prof2]}</b>\n"
        f"<i>{PROF_DESCRIPTIONS.get(prof2, '')}</i>\n\n"
        f"👇 Выбери профессию"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"🅰️ {PROF_SHORT[prof1]}", callback_data=f"pick_{prof1}"),
            InlineKeyboardButton(text=f"🅱️ {PROF_SHORT[prof2]}", callback_data=f"pick_{prof2}")
        ],
        [
            InlineKeyboardButton(text="📸 Подробнее (A)", callback_data=f"photo_{prof1}"),
            InlineKeyboardButton(text="📸 Подробнее (B)", callback_data=f"photo_{prof2}")
        ]
    ])

    await bot.send_message(chat_id, text, reply_markup=kb)
    user_data["pair"] += 1

# =========================
# "Гоу!" -> старт раунда 2
# =========================
@dp.callback_query(F.data == "go_round2")
async def go_round2(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()

    if user_id not in current_users:
        await callback.message.answer("🔄 Нажми «🔄 Старт» или /start")
        return

    await callback.message.delete()
    await bot.send_message(callback.message.chat.id, "🔥 <b>Поехали во 2 раунд!</b>")
    await show_pair(callback.message.chat.id, user_id)

# =========================
# Выбор профессии
# =========================
@dp.callback_query(F.data.startswith("pick_"))
async def pick_profession(callback: CallbackQuery):
    user_id = callback.from_user.id
    prof_id = int(callback.data.split("_")[1])
    await callback.answer()

    if user_id not in current_users:
        await callback.message.answer("🔄 Нажми «🔄 Старт» или /start")
        return

    user_data = current_users[user_id]
    if user_data["round"] == 1:
        user_data["round1_winners"].append(prof_id)
    else:
        user_data["round2_winners"].append(prof_id)

    await callback.message.delete()
    await show_pair(callback.message.chat.id, user_id)

# =========================
# Подробнее (описание + фото images/<id>.png)
# =========================
@dp.callback_query(F.data.startswith("photo_"))
async def show_photo(callback: CallbackQuery):
    prof_id = int(callback.data.split("_")[1])
    await callback.answer()

    color = COLORS.get(prof_id, "неизвестно")
    t = TYPE_DESCRIPTIONS.get(color)
    type_name = t["name"] if t else "Тип не определён"

    await callback.message.answer(
        f"📋 <b>{PROF_NAMES.get(prof_id, 'Профессия')}</b>\n\n"
        f"{PROF_DESCRIPTIONS.get(prof_id, 'Описание скоро появится')}\n\n"
        f"🎨 Цвет: <b>{color}</b>\n"
        f"💎 Тип: <b>{type_name}</b>"
    )

    try:
        photo = FSInputFile(f"images/{prof_id}.png")
        await callback.message.answer_photo(photo, caption=f"📸 <b>{PROF_NAMES.get(prof_id, '')}</b>")
    except Exception:
        await callback.message.answer("⚠️ Картинка не найдена. Проверь: images/1.png ... images/50.png")

# =========================
# Итоги — кнопка после 2 раунда
# =========================
@dp.callback_query(F.data == "show_final")
async def show_final(callback: CallbackQuery):
    user_id = callback.from_user.id
    await callback.answer()

    if user_id not in current_users:
        await callback.message.answer("🔄 Нажми «🔄 Старт» или /start")
        return

    await callback.message.delete()
    await show_results(callback.message.chat.id, user_id)

async def show_results(chat_id, user_id):
    user_data = current_users.get(user_id)
    if not user_data:
        return

    final_winners = user_data["round2_winners"]
    total = len(final_winners)
    if total == 0:
        await bot.send_message(chat_id, "Тест завершился слишком рано. Нажми «🎯 Тест ПрофКод» и начни заново.")
        current_users.pop(user_id, None)
        return

    color_count = Counter(COLORS[p] for p in final_winners)
    top3 = color_count.most_common(3)
    max_count = top3[0][1] if top3 else 0

    text = "<b>Типы профессий, которые тебе подходят после прохождения теста «ПрофКод»</b>\n\n"
    text += FINAL_INTRO_TEXT

    for i, (color, count) in enumerate(top3, 1):
        info = TYPE_DESCRIPTIONS.get(color)
        if not info:
            continue
        percent = (count / total) * 100
        prio = " 👑 <b>(приоритет)</b>" if count == max_count else ""
        text += (
            f"{i}️⃣ {info['emoji']} <b>{info['name']}</b> — {count}/{total} ({percent:.0f}%) {prio}\n"
            f"{info['desc']}\n"
            f"👉 {info['link']}\n\n"
        )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 НОВЫЙ ТЕСТ", callback_data="restart_test")]
    ])

    await bot.send_message(chat_id, text, reply_markup=kb, disable_web_page_preview=True)
    current_users.pop(user_id, None)

@dp.callback_query(F.data == "restart_test")
async def restart_test(callback: CallbackQuery):
    user_id = callback.from_user.id
    reset_user(user_id)
    await callback.answer()
    await callback.message.delete()
    await bot.send_message(callback.message.chat.id, "🚀 <b>Новый тест начался!</b>")
    await show_pair(callback.message.chat.id, user_id)

# =========================
# Запуск
# =========================
async def main():
    print("🤖 Бот запущен: @umschool_prof_bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

