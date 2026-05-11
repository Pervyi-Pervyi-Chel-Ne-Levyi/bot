import telebot
from telebot import types
import os
import threading
from flask import Flask

# ====== BOT TOKEN ======
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# ====== FLASK (для Render 24/7) ======
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

PORT = int(os.environ.get("PORT", 10000))

def run_web():
    app.run(host="0.0.0.0", port=PORT)

threading.Thread(target=run_web).start()

# ====== ВОПРОСЫ ======
questions = [
    "Испытываете ли вы трудности при объяснении грамматики на английском языке?",
    "Нужна ли вам помощь в улучшении разговорного английского?",
    "Чувствуете ли вы неуверенность при общении с учениками на английском?",
    "Хотели бы вы расширить свой словарный запас по профессиональной теме?",
    "Возникают ли у вас сложности с правильным произношением?",
    "Нужна ли вам помощь в подготовке материалов или презентаций на английском языке?",
    "Хотели бы вы улучшить навыки деловой переписки на английском?",
    "Есть ли у вас трудности с пониманием английской речи на слух?",
    "Хотели бы вы подготовиться к международным экзаменам по английскому языку?",
    "Считаете ли вы, что консультация по английскому языку поможет вам в работе?"
]

# ====== ДАННЫЕ ======
user_data = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("Да", callback_data="consult_yes"),
        types.InlineKeyboardButton("Нет", callback_data="consult_no")
    )

    bot.send_message(
        message.chat.id,
        "Здравствуйте!\n\n"
        "Я бот для оценки вашей готовности к преподаванию английского языка.\n\n"
        "Доступные команды:\n"
        "/start — начать тест\n"
        "/help — помощь\n"
        "/about — информация о боте\n"
        "/restart — пройти заново\n\n"
        "После прохождения теста вы получите результат уровня подготовки.\n\n"
        "Вам точно нужна консультация?",
        reply_markup=keyboard
    )


# ================= HELP =================
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id,
        "📌 Помощь\n\n"
        "Этот бот помогает определить вашу готовность к преподаванию английского языка.\n\n"
        "Шаги:\n"
        "1. /start\n"
        "2. Ответьте Да/Нет\n"
        "3. Введите ФИО\n"
        "4. Ответьте на 10 вопросов\n"
        "5. Получите результат\n\n"
        "Команды:\n"
        "/start /help /about /restart"
    )


# ================= ABOUT =================
@bot.message_handler(commands=['about'])
def about(message):
    bot.send_message(
        message.chat.id,
        "🤖 Consultation for Teaching\n\n"
        "Бот создан для оценки уровня готовности к преподаванию английского языка.\n\n"
        "Разработчик: @Pervyi_Pervyi_Chel_Ne_Levyi"
    )


# ================= RESTART =================
@bot.message_handler(commands=['restart'])
def restart(message):
    user_id = message.from_user.id

    if user_id in user_data:
        user_data[user_id] = {
            "fio": "",
            "q_index": 0,
            "yes": 0
        }

    bot.send_message(
        message.chat.id,
        "🔄 Тест сброшен. Нажмите /start чтобы начать заново."
    )


# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id

    if call.data == "consult_yes":
        bot.send_message(call.message.chat.id, "Хорошо! Пожалуйста, напишите ваше ФИО")
        bot.register_next_step_handler(call.message, get_name)

    elif call.data == "consult_no":
        bot.send_message(call.message.chat.id, "Хорошо, если захотите пройти позже — нажмите /start")

    elif call.data == "name_yes":
        user_data[user_id]["q_index"] = 0
        user_data[user_id]["yes"] = 0
        ask_question(call.message.chat.id, user_id)

    elif call.data == "name_no":
        bot.send_message(call.message.chat.id, "Напишите ваше ФИО заново")
        bot.register_next_step_handler(call.message, get_name)

    elif call.data in ["q_yes", "q_no"]:
        if call.data == "q_no":
            user_data[user_id]["yes"] += 1

        user_data[user_id]["q_index"] += 1
        ask_question(call.message.chat.id, user_id)


# ================= ФИО =================
def get_name(message):
    user_id = message.from_user.id

    user_data[user_id] = {
        "fio": message.text,
        "q_index": 0,
        "yes": 0
    }

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("Да", callback_data="name_yes"),
        types.InlineKeyboardButton("Нет", callback_data="name_no")
    )

    bot.send_message(
        message.chat.id,
        f"Ваше ФИО: {message.text}\nЕсли вы ошиблись — нажмите Нет",
        reply_markup=keyboard
    )


# ================= ВОПРОСЫ =================
def ask_question(chat_id, user_id):
    index = user_data[user_id]["q_index"]

    if index < len(questions):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton("Да", callback_data="q_yes"),
            types.InlineKeyboardButton("Нет", callback_data="q_no")
        )

        bot.send_message(
            chat_id,
            f"Вопрос {index + 1}/10\n\n{questions[index]}",
            reply_markup=keyboard
        )
    else:
        show_result(chat_id, user_id)


# ================= РЕЗУЛЬТАТ =================
def show_result(chat_id, user_id):
    score = user_data[user_id]["yes"]
    fio = user_data[user_id]["fio"]

    if score <= 3:
        result_text = "Вам определённо нужна консультация"
    elif score <= 6:
        result_text = "Нормально, но нужно подтянуть знания"
    else:
        result_text = "Ахуенно, уровень хороший"

    bot.send_message(
        chat_id,
        f"Результат: {fio} {score}/10\n"
        f"{result_text}\n\n"
        f"Вы можете отправить результат: @miss_liza_almaty\n\n"
        f"Бот создан: @Pervyi_Pervyi_Chel_Ne_Levyi\n"
        f"Если нужны подобные боты — пишите, по цене договоримся."
        )


# ================= ЗАПУСК =================
import time

print("Bot started")

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)
