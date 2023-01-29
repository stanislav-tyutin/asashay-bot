from ais_connector import AisSession, get_slots, create_session
from config import BOT_TOKEN, LOGIN, PASSWORD
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from threading import Thread, Event
from time import sleep
from datetime import datetime
import random
import traceback
import logging
import sys


def loop():
    global min_date
    global session
    global last_update
    while True:
        if session is None:
            session = create_session(LOGIN, PASSWORD)
            sleep(random.randrange(2, 5))
            logging.info('Session created')
            send_message_to_all('Session created')
        else:
            try:
                has_data, slots = get_slots(session)
                if has_data:
                    if len(slots) > 0:
                        new_min_date = get_min_date(slots)
                        if (min_date is None) or (min_date != new_min_date):
                            min_date = new_min_date
                            send_message_to_all('New date available: ' + datetime.strftime(min_date, '%Y-%m-%d'))
                    else:
                        if min_date is not None:
                            min_date = None
                            send_message_to_all('No dates available')

                last_update = datetime.now()

                sleep(random.randrange(30, 200))

            except Exception as e:
                traceback.print_exc()
                send_message_to_all('Here is some problems')
                logging.warning('Here is some problems')
                session = None

        sleep(1)


def get_min_date(source):
    return min(map(lambda x: datetime.strptime(x['date'], '%Y-%m-%d'), source))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    subscribed_users.add(update.effective_chat.id)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I've saved you to list")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if last_update is not None:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=datetime.strftime(last_update, '%Y-%m-%d %H:%M:%S'))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Never')


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
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    session = None
    subscribed_users = set()
    messages_stack = []
    min_date = None
    last_update = None

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    job_queue = application.job_queue
    job_queue.run_repeating(send_messages, interval=1, first=1)

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    status_handler = CommandHandler('status', status)
    application.add_handler(status_handler)

    loop_thread = Thread(target=loop)
    loop_thread.start()

    application.run_polling()

