#!/usr/bin/env python
# -*- coding: utf-8 -*-
import telebot
import redis
import config
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S')


# redis connection
try:
    redis = redis.Redis(db=0, host='localhost', port=16379)
except Exception as error:
    logging.exception(str(error), exc_info=True)
    exit(13)

# telegram bot
bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f'Привет, я бот!\n'
                          f'Могу напомнить о встрече.\n'
                          f'Все что от тебя нужно это желание и время :)\n\n'
                          f'Жми сюда /go если хочешь',
                 parse_mode='Markdown')
    logging.info(f'{message.from_user.username} pressed /start')


@bot.message_handler(commands=['go'])
def send_invitation(message):
    nick = message.from_user.username
    # message.from_user.id === message.chat.id
    chat_id = message.chat.id
    logging.info(f'{nick} pressed /go')

    redis.set(f'{nick}:go', value=chat_id)

    start_markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = telebot.types.InlineKeyboardButton('да', callback_data='yes')
    btn2 = telebot.types.InlineKeyboardButton('нет', callback_data='no')
    start_markup.add(btn1, btn2)

    bot.send_message(chat_id, 'Прислать тебе уведомление о начале?', reply_markup=start_markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    logging.info(f'{message.from_user.username} sent: `{message.text}`')
    if 'привет' in message.text.lower():
        bot.send_message(message.from_user.id, 'Привет!')
    else:
        bot.send_message(message.from_user.id, 'Не понимаю, что это значит. Если есть вопрос, то напшии моемуу '
                                               'создателю')


@bot.callback_query_handler(func=lambda call: True)
def call_handler(call):
    nick = call.from_user.username
    chat_id = call.message.chat.id

    if call.data == "yes":
        """ 
        call.from_user =>
        {'id': 463486146, 'is_bot': False, 'first_name': 'Alex', 'username': 'Faradek', 'last_name': 'Velm', 
        'language_code': 'ru', 'can_join_groups': None, 'can_read_all_group_messages': None, 
        'supports_inline_queries': None}
        """
        logging.info(f'{nick} согласен.')

        redis.set(f'{nick}:meet_able', value=chat_id)
        bot.send_message(call.message.chat.id, text=f"Огонь! Как только смогу, то пошлю тебе ссылку.")

    elif call.data == "no":
        logging.info(f'{nick} отказался.')
        redis.delete(f'{nick}:meet_able')
        bot.send_message(call.message.chat.id, text="Хорошо, я понял. Ты не хочешь.")


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=3000, long_polling_timeout=3000)
