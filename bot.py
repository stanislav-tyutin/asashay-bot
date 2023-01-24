from ais_connector import AisSession, get_slots
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from threading import Thread
from time import sleep
from datetime import datetime
import random


def loop():
    global min_date
    global session
    global last_update
    while True:
        if session is not None:
            try:
                slots = get_slots(session)
                new_min_date = get_min_date(slots)
                print(new_min_date)
                if (min_date is None) or (min_date != new_min_date):
                    min_date = new_min_date
                    send_message_to_all('New date is available: ' + datetime.strftime(min_date, '%Y-%m-%d'))

                last_update = datetime.now()
                sleep(random.randrange(500, 800))
            except:
                send_message_to_all('Here is some problems')
                session = None
        sleep(1)


def get_min_date(source):
    return min(map(lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), source))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribed_users.append(update.effective_chat.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I've saved you to list")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=datetime.strftime(min_date, '%Y-%m-%d %H:%M:%S'))


async def set_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global session
    value = context.args[0]
    if value is not None:
        session = AisSession(value)
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Session saved')
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Error')


async def send_messages(context: ContextTypes.DEFAULT_TYPE):
    while len(messages_stack) > 0:
        msg = messages_stack.pop()
        await context.bot.send_message(chat_id=msg['chat_id'], text=msg['text'])


def send_message(chat_id, text):
    messages_stack.append(dict(chat_id=chat_id, text=text))


def send_message_to_all(text):
    for user_id in subscribed_users:
        send_message(user_id, text)


if __name__ == '__main__':
    BOT_TOKEN = ''
    session: AisSession = None
    subscribed_users = []
    messages_stack = []
    min_date: datetime = None
    last_update: datetime = None

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    job_queue = application.job_queue
    job_queue.run_repeating(send_messages, interval=1, first=1)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    set_session_handler = CommandHandler('set_session', set_session)
    application.add_handler(set_session_handler)

    status_handler = CommandHandler('status', status)
    application.add_handler(status_handler)

    loop_thread = Thread(target=loop)
    loop_thread.start()

    application.run_polling()

