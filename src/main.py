#!/bin/env python3.9

# import os
# from dotenv import load_dotenv
# from telegram.ext import Updater, CommandHandler

# import telegam

# load_dotenv()

# BOT_TOKEN = os.getenv('BOT_TOKEN')


# # def hello(bot, updater):
    # # url = 'https://img.freepik.com/free-photo/the-cat-on-white-background_155003-15381.jpg?w=2000'
    # # chat_id = updater.message.chat_id
    # # bot.send_photo(chat_id=chat_id, photo=url)


# def start(update: Update, context: CallbackContext):
    # # chat_id = updater.chat_id
    # context.bot.send_message()


# def main():
    # updater = Updater(token=BOT_TOKEN)
    # dp = updater.dispatcher
    # dp.add_handler(CommandHandler('start', start))
    # updater.start_polling()
    # updater.idle()


# if __name__ == "__main__":
    # main()

import os
from dotenv import load_dotenv
from flask import Flask
from flask import request
from flask import Response
import requests

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
app = Flask(__name__)


def parse_message(message):
    print("message-->",message)
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id,txt


def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }

    return requests.post(url,json=payload)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        msg = request.get_json()

        chat_id,txt = parse_message(msg)
        if txt == "hi":
            tel_send_message(chat_id,"Hello!!")
        else:
            tel_send_message(chat_id,'from webhook')

        return Response('ok', status=200)
    else:
        return "<h1>Welcome!</h1>"


if __name__ == '__main__':
   app.run(debug=True)

