from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import bot_token, QIWI_ACCOUNT
from states import Token, Pay, Mailing, GiveAccess, OnePay
from keyboards import main_keyboard, cancel_keyboard, notpayed_keyboard, pay_keyboard, admin_keyboard, \
    choice_pay_keyboard
from utils import admin_cheak, write_id, set_subending_time, validate_subscription, add_tokens, ThreadWithReturnValue, \
    get_balances, send_balances, get_subending_time, read_ids, send_message
from qiwi import send_balance
from paynament import cheak_payment

bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.answer("Привет,чтобы пользоваться ботом, необходимо оплатить доступ",
                         reply_markup=notpayed_keyboard if not admin_cheak(message.chat.id) else admin_keyboard)
    write_id(message.from_user.id, message.from_user.username)


@dp.message_handler(state="*", text_contains='Отмена')
async def stop_command(message: types.Message, state: FSMContext):
    await message.answer(text="Главное меню",
                         reply_markup=main_keyboard if not admin_cheak(message.chat.id) else admin_keyboard)
    await state.finish()


@dp.message_handler(text='Купить доступ')
async def buy_access(message: types.Message):
    await message.answer(
        f'Покупка доступа к боту:\n1 день - 10 рублей\nНомер: {QIWI_ACCOUNT}\nКомментарий: {message.chat.id}',
        reply_markup=pay_keyboard)


@dp.callback_query_handler(text='confirm_paynament')
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    payed_time = cheak_payment(str(callback_query.from_user.id))
    if payed_time:
        set_subending_time(str(callback_query.from_user.id), payed_time)
        await bot.send_message(callback_query.from_user.id, 'Спасибо за покупку!', reply_markup=main_keyboard)
    else:
        await bot.send_message(callback_query.from_user.id, 'Оплата не поступила, попробуйте позже.Или напишите владельцу')
    await bot.answer_callback_query(callback_query.id)


@dp.message_handler(text="Добавить кошельки🔰")
async def upload_tokens(message: types.Message):
    if validate_subscription(str(message.from_user.id)):
        await message.answer("Отправь телефон:token", reply_markup=cancel_keyboard)
        await Token.waiting_to_token_value.set()
    else:
        await message.answer("Для использования бота необходима подписка")


@dp.message_handler(state=Token.waiting_to_token_value, content_types=types.ContentTypes.TEXT)
async def listen(message: types.Message, state: FSMContext):
    tokens = message.text.split('\n')
    tokens = add_tokens(str(message.from_user.id), tokens)
    await message.answer(f"Успешно загружено {len(tokens)} токен(ов)",
                         reply_markup=main_keyboard if not admin_cheak(message.chat.id) else admin_keyboard)
    await state.finish()


@dp.message_handler(text="Узнать баланс👁")
async def get_balance(message: types.Message):
    if validate_subscription(str(message.from_user.id)):
        await message.answer("Парсю, жди")
        thread = ThreadWithReturnValue(target=get_balances, args=(str(message.from_user.id),))
        thread.start()
    else:
        await message.answer("Для использования бота необходима подписка")


@dp.message_handler(text="Сделать перевод💵")
async def start_send_balance(message: types.Message):
    if validate_subscription(str(message.from_user.id)):
        await message.answer("Выберите", reply_markup=choice_pay_keyboard)
    else:
        await message.answer("Для использования бота необходима подписка")


@dp.callback_query_handler(text="all_qiwi")
async def all_qiwis_pay(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id, text="Номер для перевода:", reply_markup=cancel_keyboard)
    await Pay.waiting_to_pay_values.set()


@dp.callback_query_handler(text="one_qiwi")
async def one_qiwis_pay(callback_query: types.CallbackQuery):
    await bot.send_message(chat_id=callback_query.from_user.id, text="Введите данные кошелька (phone:token)", reply_markup=cancel_keyboard)
    await OnePay.waiting_data.set()


@dp.message_handler(state=Pay.waiting_to_pay_values, content_types=types.ContentTypes.TEXT)
async def listen(message: types.Message, state: FSMContext):
    phone = message.text
    await message.answer("Начата отправка", reply_markup=main_keyboard)
    send_balances(str(message.from_user.id), phone)
    await state.finish()


@dp.message_handler(state=OnePay.waiting_data, content_types=types.ContentTypes.TEXT)
async def listen(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['data'] = message.text
    await message.answer("Номер на который нужен перевод")
    await OnePay.waiting_phone.set()


@dp.message_handler(state=OnePay.waiting_phone, content_types=types.ContentTypes.TEXT)
async def listen(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data = data['data']
        phone = message.text
    respone = send_balance(*data.split(':'), phone)
    if respone != "Невалидный кошелек":
        await message.answer(f"Было отправлено {respone}Р", reply_markup=main_keyboard)
    else:
        await message.answer(respone, reply_markup=main_keyboard)
    await state.finish()


@dp.message_handler(text="Подписка🗝")
async def check_subscribe(message: types.Message):
    await message.answer(get_subending_time(str(message.from_user.id), reform=True))


@dp.message_handler(text_endswith=['Рассылка', 'рассылка'])
async def mailing_command(message: types.Message):
    if admin_cheak(message.chat.id):
        await message.answer("Введите текст для рассылки", reply_markup=cancel_keyboard)
        await Mailing.waiting_text.set()


@dp.message_handler(state=Mailing.waiting_text, content_types=types.ContentTypes.TEXT)
async def mailing(message: types.Message, state: FSMContext):
    text = message.text
    users = read_ids()
    sended = 0
    for user in users:
        if send_message(user, text)[6:][:4] == 'true':
            sended += 1
    await message.answer(f"Оправленно сообщение в {sended} чата", reply_markup=admin_keyboard)
    await state.finish()


@dp.message_handler(text='Выдать доступ')
async def get_give_access_data(message: types.Message):
    if admin_cheak(message.chat.id):
        await message.answer("Введите айди пользователя, которому хотите выдать доступ.", reply_markup=cancel_keyboard)
        await GiveAccess.waiting_id.set()


@dp.message_handler(state=GiveAccess.waiting_id, content_types=types.ContentTypes.TEXT)
async def listing(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['id'] = message.text
    await message.answer("На сколько выдать подписку (в секундах)")
    await GiveAccess.waiting_time.set()


@dp.message_handler(state=GiveAccess.waiting_time, content_types=types.ContentTypes.TEXT)
async def give_access(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_id = str(data['id'])
        subtime = int(message.text)
    try:
        set_subending_time(user_id, subtime)
        await bot.send_message(chat_id=user_id, text="Вам был выдан доступ от администратора",
                               reply_markup=main_keyboard)
        await message.answer("Успешно", reply_markup=admin_keyboard)
    except:
        await message.answer("Ошибка, пользователя нету в базе.", reply_markup=admin_keyboard)
    await state.finish()


@dp.message_handler(text_contains='DB')
async def info(message: types.Message):
    if admin_cheak(message.chat.id):
        await bot.send_document(message.chat.id, open('data/chat_ids.json', 'r'))
        await bot.send_document(message.chat.id, open('data/DB.json', 'r'))

if __name__ == '__main__':
    executor.start_polling(dp)
