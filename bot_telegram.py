import logging, string, json, constants
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from random import choice
from time import sleep
from create_bot import *
from main_keyboard import KeyboardHandler
from inline_keyboard import InlineKeyboardHandler
from datetime import datetime
from watermark.watermark import create_watermark
from weather.weather_handler import register_handlers_weather
from finance.finance_handler import register_handlers_finance

logging.basicConfig(level=logging.INFO)


dp.middleware.setup(LoggingMiddleware())


params = {
    'vote_up': 0,
    'vote_down': 0
}



async def on_startup(_):
    with open('static/params.json') as f:
        start_up_params = json.load(f)
        params['vote_up'] = start_up_params['vote_up']
        params['vote_down'] = start_up_params['vote_down']


async def on_shutdown():
    with open('static/params.json', 'w') as f:
        json.dump(params, f)


def check_words(fn):
    async def inner(msg: types.Message, state: FSMContext, *args, **kwargs):
        if any(word in msg.text.lower().
                translate(str.maketrans('', '', string.punctuation)) for word in constants.BAD_WORDS):
            await msg.reply(choice(constants.ANSWER_FOR_BAD_WORDS))
            await state.finish()
            sleep(3)
            await msg.delete()
        else:
            await fn(msg, state, *args, **kwargs)
    return inner


@dp.message_handler(commands=['start'])
async def start_cmd(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Выберите что-то из пункта меню',
                           reply_markup=KeyboardHandler.main_kb)


#     **********************************************
@dp.message_handler(Text('💧Нанести водяной знак'))
async def make_watermark(msg: types.Message):
    await FSMStates.image_for_watermark.set()
    await msg.reply('Выберите картинку', reply_markup=KeyboardHandler.undo_kb)


@dp.message_handler(content_types=['photo'], state=FSMStates.image_for_watermark)
async def input_photo(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        now = datetime.now()
        name = f'static/photos/img-{now.year}-{now.month}-{now.day}--{now.hour}-{now.minute}.jpg'
        await msg.photo[-1].download(name)
        data['image_for_watermark'] = name
        await FSMStates.next()
        await msg.reply('Теперь введите текст для водяного знака (не больше 20 символов',
                        reply_markup=KeyboardHandler.undo_kb)


@dp.message_handler(state=FSMStates.watermark_word)
@check_words
async def input_text(msg: types.Message, state: FSMContext, *args, **kwargs):
    async with state.proxy() as data:
        if len(msg.text) > 20:
            await msg.reply('Длина строки больше 20 символов, введти другой текст')
            await FSMStates.watermark_word.state
        elif msg.text == '☠Отменить':
            await state.finish()
            await msg.reply('Отменяем...', reply_markup=KeyboardHandler.main_kb)
        else:
            data['watermark_word'] = msg.text
            await msg.reply('Ваши данные приняты, ожидайте картинку', reply_markup=KeyboardHandler.main_kb)
            await bot.send_photo(msg.from_user.id, create_watermark(data["image_for_watermark"], data["watermark_word"]))
        await state.finish()






async def step_back(msg: types.Message):
    await msg.reply('Переходим в прошлое меню', reply_markup=history.get())


async def inline_test(msg: types.Message):
    message = f'👍 - {params["vote_up"]}, 👎 - {params["vote_down"]}'
    await msg.reply('Для отмены выберите пункт меню Отменить', reply_markup=KeyboardHandler.undo_kb)
    inline_msg = await bot.send_message(msg.from_user.id, message, reply_markup=InlineKeyboardHandler.vote_ikb)
    params['msg_id'] = inline_msg.message_id


async def cancel_handler(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if params.get('msg_id'):
        try:
            await bot.delete_message(msg.from_user.id, params['msg_id'])
        except:
            pass
    await on_shutdown()
    if current_state:
        await state.finish()
    await msg.reply('Отменяем...', reply_markup=KeyboardHandler.main_kb)


async def vote_handler(callback: types.CallbackQuery):
    await callback.answer()
    vote = callback.data
    print(vote)
    if vote == 'like':
        params['vote_up'] += 1
    elif vote == 'dislike':
        params['vote_down'] += 1

    msg = f'👍 {params["vote_up"]}, 👎 {params["vote_down"]}'
    await bot.edit_message_text(msg, callback.from_user.id,
                                callback.message.message_id, reply_markup=InlineKeyboardHandler.vote_ikb)


@check_words
async def echo_send(msg: types.Message, *args, **kwargs):
    await msg.answer(msg.text)


def register_handlers(dp: Dispatcher):
    register_handlers_weather(dp)
    register_handlers_finance(dp)
    # dp.register_message_handler(vote_handler, lambda msg: msg.data in ['like', 'dislike'])
    dp.register_message_handler(inline_test, Text('Inline button test'))
    dp.register_message_handler(step_back, Text('⏪Назад'))
    dp.register_message_handler(echo_send)
    dp.register_message_handler(cancel_handler, state='*', regexp='☠Отменить')


if __name__ == '__main__':
    register_handlers(dp)
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)