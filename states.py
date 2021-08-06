from aiogram.dispatcher.filters.state import State, StatesGroup


class Token(StatesGroup):
    waiting_to_token_value = State()


class Pay(StatesGroup):
    waiting_to_pay_values = State()


class Mailing(StatesGroup):
    waiting_text = State()


class GiveAccess(StatesGroup):
    waiting_id = State()
    waiting_time = State()


class OnePay(StatesGroup):
    waiting_data = State()
    waiting_phone = State()
