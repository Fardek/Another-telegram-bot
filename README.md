# Simple telegram bot



Структура на VPS.

### redis
```
ubuntu@avelmatkin:~/telegram_bot$ tree /opt/redis/
/opt/redis/
├── data
│   ├── bases
│   │   ├── appendonly.aof
│   │   └── dump.rdb
│   └── log
│       └── redis-server.log
└── etc
    └── redis.conf
```

## Для запуска.

Нужно склонировать проект на свою машину (локальную или удаленную по типу VPS).

### Стартануть redis
Проверьте, что находитесь в директории проекта, а файлы для redis распихали по папкам согласно указанного выше и запустите:
```
docker-compose up -d
```
Вы подняли инстанс redis. Он нам нужен для хранения ника и номера чата, в котором клиеннт общается с ботом.

### Стартануть бота
Следом запустите самого бота:
```
python3 ./run.py
```
Он логирует действия клиента в stdout, то есть на экран консоли.  
Можно перенаправить выводв какой-нибудь файл. По типу:
```
python3 ./run.py &> run.log
```
Но такая конструкция будет перезаписывать файл лога при каждомо запуске.
Поэтому я предпочитаю делать так:
```
ubuntu@avelmatkin:~/telegram_bot$ while :; do ./run.py 1>> run.log 2>&1 && sleep 10; done
```

И запускать это всё в сессии tmux. (надо переделать на юнит systemd)

## Для отправки клиентам нужной ссылки на мероприятие.
Используй скрипт sender.py из этого же проекта.
У него есть help:
```
python3 ./sender.py --help

usage: sender.py [-h] {send_meet,send_custom_message} ...

Рассылка

positional arguments:
  {send_meet,send_custom_message}
                        use only one
    send_meet           Send meeting link
    send_custom_message
                        Send custom message for all from "go"-group

optional arguments:
  -h, --help            show this help message and exit
```

Совершить рассылку можно так:
```
fardek@fardek-qq:~/hobby/Another-telegram-bot$ python3 ./sender.py send_meet
14-Nov-22 11:34:25 INFO: meet_able: []
14-Nov-22 11:34:25 INFO: people able meet: {}
14-Nov-22 11:34:25 WARNING: Никого согласных на встречу не нашлось.
```
В данном случае у нас нет согластных на рассылку клиентов, поэтому вернулись пустые множества.

