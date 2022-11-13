#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
from run import redis, bot, logging


def get_persons(keys: list, choose: str) -> dict:
    # Формируем dict( telegram_nick: message.chat_id )
    persons = {}
    for person in keys:
        nick, _ = person.split(':')
        chat_id = redis.get(f'{nick}:{choose}').decode('utf-8', errors='ignore')
        persons[nick] = chat_id
    return persons


def send_to_meet():
    """ Рассылка желающим """

    # Список согласившихся получить уведомление
    meet_able = redis.keys('*:meet_able')
    meet_able = list(map(bytes.decode, meet_able))
    logging.info(f'meet_able: {meet_able}')

    # Формируем dict( telegram_nick: message.chat_id )
    persons = get_persons(meet_able, 'meet_able')
    logging.info(f'people able meet: {persons}')

    if not persons:
        logging.warning('Никого согласных на встречу не нашлось.')
        exit(1)

    for nick, chat_id in persons.items():
        bot.send_message(chat_id=chat_id, text=f'Вот твоя ссылка https//ya.ru')
        logging.info(f'We sent to @{nick} link')


def send_custom_message() -> None:
    """ Рассылка всем, кто не удалил бота """

    text = 'Привет! :) \n' \
           'Спешу пожелать тебе счастливого Нового года и сказать, ' \
           'что я ухожу вместе с тобой отдыхать до конца праздников (10.01). \n' \
           'Спишемся в январе!'

    go = redis.keys('*:go')
    go = list(map(bytes.decode, go))
    persons_go = get_persons(go, 'go')

    for nick, chat_id in persons_go.items():
        bot.send_message(chat_id=chat_id, text=text)
        logging.info(f'send_custom_message to {nick}')


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Рассылка")
    subparsers = parser.add_subparsers(help='use only one', dest='subcommand')

    invitation = subparsers.add_parser('send_meet', help='Send meeting link')
    invitation.set_defaults(func=send_to_meet)

    custom_message = subparsers.add_parser('send_custom_message', help='Send custom message for all from "go"-group')
    custom_message.set_defaults(func=send_custom_message)
    return parser


def main():
    args = get_parser().parse_args()
    if not hasattr(args, "func"):
        return get_parser().print_help()
    else:
        return args.func()


if __name__ == "__main__":
    main()
