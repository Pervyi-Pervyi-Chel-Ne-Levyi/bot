import telebot
import os
import threading
from flask import Flask

# ================= BOT =================
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# ================= WEB SERVER (для Render) =================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running"

PORT = int(os.environ.get("PORT", 10000))

def run_web():
    app.run(host="0.0.0.0", port=PORT)

threading.Thread(target=run_web).start()

# ================= ВОПРОСЫ =================
questions = [
   "Трудно ли вам разговаривать на английском языке?",
   "Понимаете ли вы английскую речь с трудом?",
   "Часто ли вы не можете подобрать нужные слова при разговоре?",
   "Ошибаетесь ли вы часто при построении английских предложений",
   "Сложно ли вам говорить без перевода в голове?",
   "Испытываете ли вы страх или неуверенность при разговоре на английском?",
   "Трудно ли вам понимать английские фильмы или видео без субтитров?",
   "Забываете ли вы английские слова, которые раньше знали?",
   "Сложно ли вам начать разговор на английском с человеком?",
   "Чувствуете ли вы, что ваш уровень английского недостаточен для общения?"
]

user_data = {}

# ================= START =================
@bot.message_handler(commands=['start'])
def start(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton("Да", callback_data="consult_yes"),
        telebot.types.InlineKeyboardButton("Нет", callback_data="consult_no")
    )

    bot.send_message(
        message.chat.id,
        "Здравствуйте!\n\n"
        "Я бот для оценки вашей готовности к преподаванию английского языка.\n\n"
        "Доступные команды:\n"
        "/help — помощь\n"
        "/about — информация о боте\n"
        "/restart — пройти заново\n\n"
        "Вы хотите пройти тест?",
        reply_markup=keyboard
    )

# ================= HELP =================
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Помощь: /start /about /restart")

# ================= ABOUT =================
@bot.message_handler(commands=['about'])
def about(message):
    bot.send_message(message.chat.id, "Бот для теста уровня английского")

# ================= RESTART =================
@bot.message_handler(commands=['restart'])
def restart(message):
    user_id = message.from_user.id
    user_data[user_id] = {"fio": "", "q_index": 0, "yes": 0}
    bot.send_message(message.chat.id, "Сброшено. Нажмите /start")

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id

    if call.data == "consult_yes":
        bot.send_message(call.message.chat.id, "Введите ФИО")
        bot.register_next_step_handler(call.message, get_name)

    elif call.data == "consult_no":
        bot.send_message(call.message.chat.id, "Ок 👍")

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

    ask_question(message.chat.id, user_id)

# ================= ВОПРОСЫ =================
def ask_question(chat_id, user_id):
    index = user_data[user_id]["q_index"]

    if index < len(questions):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton("Да", callback_data="q_yes"),
            telebot.types.InlineKeyboardButton("Нет", callback_data="q_no")
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
        text = "Вам нужна консультация"
    elif score <= 6:
        text = "Средний уровень"
    else:
        text = "Хороший уровень"

    bot.send_message(chat_id, f"{fio}\n{score}/10\n{text}")

# ================= ЗАПУСК =================
print("Bot started")
bot.infinity_polling()