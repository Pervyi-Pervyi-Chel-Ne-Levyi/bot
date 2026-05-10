import telebot
import os

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# ====== ВОПРОСЫ ======
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
        "/help — помощь\n"
        "/about — информация о боте\n"
        "/restart — пройти заново\n\n"
        "После прохождения теста вы получите результат уровня подготовки.\n\n"
        "Вы уверены что хотите пройти тест чтобы узнать нужна ли вам консультация?",
        reply_markup=keyboard
    )


# ================= HELP =================
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(
        message.chat.id,
        "Помощь\n\n"
        "Этот бот помогает определить вашу готовность к преподаванию английского языка.\n\n"
        "Шаги:\n"
        "1. /start\n"
        "2. Ответьте Да/Нет\n"
        "3. Введите ФИО\n"
        "4. Ответьте на 10 вопросов\n"
        "5. Получите результат\n\n"
        "Команды:\n"
        "/start\n"
        "/help\n"
        "/about\n"
        "/restart\n"
    )


# ================= ABOUT =================
@bot.message_handler(commands=['about'])
def about(message):
    bot.send_message(
        message.chat.id,
        "Consultation for Teaching\n\n"
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
        "Тест сброшен. Нажмите /start чтобы начать заново."
    )


# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id

    if call.data == "consult_yes":
        bot.send_message(call.message.chat.id, "Хорошо! Пожалуйста, напишите ваше ФИО")
        bot.register_next_step_handler(call.message, get_name)

    elif call.data == "consult_no":
        bot.send_message(call.message.chat.id, "Хорошо, если захотите пройти позже - нажмите /start")

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
        result_text = "Отличный уровень знаний но консультация не помешает"

    bot.send_message(
        chat_id,
        f"Результат: {fio}\n"
        f"{score}/10\n"
        f"{result_text}\n\n"
        f"Вы можете отправить результат: @miss_liza_almaty\n\n"
        f"Бот создан: @Pervyi_Pervyi_Chel_Ne_Levyi\n"
        f"Если нужны подобные боты — пишите, по цене договоримся.\n"
        f"Если вы хотите перепройти тест введите /restart ."
    )


# ================= ЗАПУСК =================
bot.polling(none_stop=True)
