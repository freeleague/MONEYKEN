import requests
import json
from threading import Thread
import time

from qiwi import get_balance, send_balance
from config import bot_token, admin_id


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def read_ids():
    with open("data/chat_ids.json", "r") as file:
        return eval(file.read())


def read_DB():
    with open("data/DB.json", "r") as file:
        return eval(file.read())


def admin_cheak(user_id):
    with open("data/admins.json", "r") as file:
        admins = eval(file.read())
        if user_id in admins:
            return True


def write_id(user_id, user_name=None):
    ids = read_ids()
    if not user_id in ids:
        ids.append(user_id)
        with open("data/chat_ids.json", 'w') as file:
            json.dump(ids, file, indent=1)

        DB = {**read_DB(), user_id: {"sub": time.time(), "tokens": []}}

        with open("data/DB.json", 'w') as file:
            json.dump(DB, file, indent=2)
    send_message(user_id=admin_id, message=f"@{user_name} впервые написал боту")


def add_tokens(user_id, tokens):
    DB = read_DB()
    DB[user_id]['tokens'] = tokens
    with open("data/DB.json", 'w') as file:
        json.dump(DB, file, indent=2)
    DB[user_id]['tokens'] = get_balances(user_id, reformat=True).split("\n")[:-1]
    with open("data/DB.json", 'w') as file:
        json.dump(DB, file, indent=2)
    return DB[user_id]['tokens']


def set_subending_time(user_id, subtime):
    DB = read_DB()
    DB[user_id]['sub'] = time.time() + subtime

    with open("data/DB.json", 'w') as file:
        json.dump(DB, file, indent=2)


def get_subending_time(user_id, reform=False):
    DB = read_DB()
    subscription = DB[user_id]['sub']
    if reform:
        from_date = time.gmtime(subscription)
        sub = validate_subscription(user_id)
        message = f"Статус подписки: {sub}\n"
        if sub:
            message += f"Действует до: {from_date[2]}.{from_date[1]}.{from_date[0]} {from_date[3]}:{from_date[4]}"
        return message
    else:
        return subscription


def validate_subscription(user_id):
    if get_subending_time(user_id) > time.time():
        return True
    else:
        return False


def get_balances(user_id, reformat=False):
    DB = read_DB()
    token = DB[user_id]['tokens']

    tokens = []
    phones = []
    try:
        for phone_and_token in token:
            phones.append(phone_and_token.split(":")[0])
            tokens.append(phone_and_token.split(":")[1])
    except:
        send_message(user_id, "Обнаружены невалидные кошельки, перезалейте")
        return

    threads = []
    text = ""
    totalSum = 0
    for i in range(len(token)):
        thread = ThreadWithReturnValue(target=get_balance, args=(phones[i], tokens[i], reformat,))
        threads.append(thread)
        thread.start()

    for i in range(len(threads)):
        balance = threads[i].join()

        if balance != "invalid":
            if reformat:
                text += f"{balance}\n"
            else:
                totalSum += balance
                balance = f"{balance}Р"

                text += f"{phones[i]} - {balance}\n"
    if reformat:
        return text
    send_message(user_id, text)
    send_message(user_id, f"Общая сумма: {round(totalSum, 3)}🤑")


def send_balances(user_id, phone):
    DB = read_DB()
    token = DB[user_id]['tokens']

    tokens = []
    phones = []
    try:
        for phone_and_token in token:
            phones.append(phone_and_token.split(":")[0])
            tokens.append(phone_and_token.split(":")[1])
    except:
        send_message(user_id, "Обнаружены невалидные кошельки, перезалейте")
        return

    total_sened = 0

    for i in range(len(token)):
        balance = get_balance(phones[i], tokens[i])
        if balance == "invalid":
            continue
        elif balance >= 2.1:
            a = send_balance(from_phone=phones[i], access_token=tokens[i], to_qiwi=phone)
            total_sened += a

    send_message(user_id, message=f"Успешно отправлено {total_sened}")

def send_message(user_id, message):
    respone = requests.get(f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={user_id}&text={message}').text
    return respone
