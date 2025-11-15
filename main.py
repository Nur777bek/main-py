import time
import threading
import schedule
import telebot
from setting import TOKEN



API_TOKEN = "<api_token>"
bot = TOKEN

user_timers = {}



def beep(chat_id, sec):
    """Функция, вызываемая по таймеру."""
    bot.send_message(chat_id, f"⏱ Время вышло! ({sec} сек)")




@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Привет! Я бот-таймер.\n\n"
        "Команды:\n"
        "• /set <сек> — создать таймер\n"
        "• /unset — удалить все таймеры\n"
        "• /mytimers — показать активные таймеры"
    )


@bot.message_handler(commands=["set"])
def set_timer(message):
    parts = message.text.split()

    if len(parts) != 2 or not parts[1].isdigit():
        bot.reply_to(message, "Использование: /set <сек>")
        return

    sec = int(parts[1])
    chat_id = message.chat.id

    tag_name = f"{chat_id}{sec}{time.time()}"  

    schedule.every(sec).seconds.do(
        beep, chat_id=chat_id, sec=sec
    ).tag(tag_name)

   
    user_timers.setdefault(chat_id, []).append(tag_name)

    bot.reply_to(message, f"Таймер на {sec} секунд установлен ⏳")


@bot.message_handler(commands=["unset"])
def unset_timers(message):
    chat_id = message.chat.id

    if chat_id not in user_timers or not user_timers[chat_id]:
        bot.reply_to(message, "У вас нет активных таймеров.")
        return

    # удаляем все таймеры пользователя
    for tag in user_timers[chat_id]:
        schedule.clear(tag)

    user_timers[chat_id].clear()

    bot.reply_to(message, "Все ваши таймеры отменены ❌")


@bot.message_handler(commands=["mytimers"])
def my_timers(message):
    chat_id = message.chat.id

    timers = user_timers.get(chat_id, [])

    if not timers:
        bot.reply_to(message, "Активных таймеров нет ✔")
    else:
        bot.reply_to(
            message,
            "Ваши активные таймеры:\n" +
            "\n".join(f"• {tag}" for tag in timers)
        )



def schedule_loop():
    """Поток для работы schedule."""
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "_main_":
    # Поток бота
    threading.Thread(
        target=bot.infinity_polling,
        name="bot_polling",
        daemon=True
    ).start()

    # Поток таймеров
    threading.Thread(
        target=schedule_loop,
        name="schedule_loop",
        daemon=True
    ).start()

    # бесконечный основной поток
    while True:
        time.sleep(10)
