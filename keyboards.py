from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

notpayed_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add("Купить доступ")

pay_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Я оплатил.', callback_data="confirm_paynament"))

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add("Добавить кошельки🔰").add("Узнать баланс👁").insert("Сделать перевод💵").add("Подписка🗝")

admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add("Рассылка").insert("Выдать доступ").add("Добавить кошельки🔰").add("Узнать баланс👁").insert("Сделать перевод💵").add("Подписка🗝")

cancel_keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add("Отмена")

choice_pay_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton("Со всех кошелей", callback_data="all_qiwi")).add(InlineKeyboardButton("С одного кошеля", callback_data="one_qiwi"))