from utils import read_DB, send_message
from qiwi import get_balance
import json
from time import sleep
from threading import Thread
from config import admin_id

balances = []


def cheaking_balance(user, phone, token, balance):
    new_balance = get_balance(phone, token)

    if balance == "invalid":
        send_message(user, f"{phone} стал невалидным и был удален из базы,возможно,это ошибка.Попробуйте перезалить")
        DB[user]['tokens'].remove(DB[user]['tokens'][DB[user]['tokens'].index(f"{phone}:{token}:{balance}")])
        with open("data/DB.json", 'w') as file:
            json.dump(DB, file, indent=2)
        return

    elif new_balance == "invalid":
        sleep(60)

    if float(balance) != new_balance:

        send_message(user, f"{phone} Обнаружено изменение!\n{balance} => {new_balance}")
        send_message(admin_id, f"{phone} Обнаружено изменение!\n{balance} => {new_balance}")
        DB[user]['tokens'][DB[user]['tokens'].index(f"{phone}:{token}:{balance}")] = f"{phone}:{token}:{new_balance}"

        with open("data/DB.json", 'w') as file:
            json.dump(DB, file, indent=2)


while True:
    DB = read_DB()
    for user in DB:
        for token in DB[user]['tokens']:
            Thread(target=cheaking_balance, args=(user, *token.split(':'),)).start()
    sleep(15)
