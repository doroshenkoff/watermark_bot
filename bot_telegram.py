import logging
import os
from utils import weather
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
import constants
from random import choice
import string
from time import sleep
from utils import WeatherHandler, currency_foreign
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboard import KeyboardHandler
from datetime import datetime
from watermark import create_watermark

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN_TELEGRAM'))

dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

weather_params = WeatherHandler()

params = {
    'back': KeyboardHandler.kb_client
}


class FSMStates(StatesGroup):
    city = State()
    image_for_watermark = State()
    watermark_word = State()



async def on_startup(_):
    pass


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
                           reply_markup=KeyboardHandler.kb_client)


@dp.message_handler(regexp='🌡Температура воздуха')
async def get_simple_weather(msg: types.Message):
    await bot.send_message(msg.from_user.id, weather(weather_params),
                           reply_markup=KeyboardHandler.kb_client)


@dp.message_handler(regexp='☔🌢🌅Полная информация')
async def get_full_weather(msg: types.Message):
    await bot.send_message(msg.from_user.id, weather(weather_params, True),
                           reply_markup=KeyboardHandler.kb_client)


@dp.message_handler(regexp='☀Погода')
async def get_weather(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Выберите расположение', reply_markup=KeyboardHandler.location_client)


@dp.message_handler(regexp='🌃Киев')
async def handle_kiev(message: types.Message):
    weather_params.city = 'Kiev'
    weather_params.lat = None
    await message.answer('Выберите вид отображения погоды', reply_markup=KeyboardHandler.weather_client)


@dp.message_handler(regexp='🏞Выберите населенный пункт')
async def handle_kiev(message: types.Message):
    await FSMStates.city.set()
    await message.reply('Введите город')


@dp.message_handler(state=FSMStates.city)
async def input_city(msg: types.Message, state: FSMContext):
    weather_params.lat = None
    async with state.proxy() as data:
        data['city'] = msg.text
        weather_params.city = data['city']
        await msg.answer('Выберите вид отображения погоды', reply_markup=KeyboardHandler.weather_client)
    await state.finish()


#     **********************************************
@dp.message_handler(regexp='💧Нанести водяной знак')
async def make_watermark(msg: types.Message):
    await FSMStates.image_for_watermark.set()
    await msg.reply('Выберите картинку', reply_markup=KeyboardHandler.undo_client)


@dp.message_handler(content_types=['photo'], state=FSMStates.image_for_watermark)
async def input_photo(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        now = datetime.now()
        name = f'static/photos/img-{now.year}-{now.month}-{now.day}--{now.hour}-{now.minute}.jpg'
        await msg.photo[-1].download(name)
        data['image_for_watermark'] = name
        await FSMStates.next()
        await msg.reply('Теперь введите текст для водяного знака (не больше 20 символов')


@dp.message_handler(state=FSMStates.watermark_word)
@check_words
async def input_text(msg: types.Message, state: FSMContext, *args, **kwargs):
    async with state.proxy() as data:
        if len(msg.text) > 20:
            await msg.reply('Длина строки больше 20 символов, введти другой текст')
            await FSMStates.watermark_word.state
        else:
            data['watermark_word'] = msg.text
            await msg.reply('Ваши данные приняты, ожидайте картинку', reply_markup=KeyboardHandler.kb_client)
            await bot.send_photo(msg.from_user.id, create_watermark(data["image_for_watermark"], data["watermark_word"]))
        await state.finish()

#    ******************************************************************************


@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    weather_params.lat = message.location.latitude
    weather_params.lon = message.location.longitude
    await message.answer('Выберите вид отображения погоды', reply_markup=KeyboardHandler.weather_client)


@dp.message_handler(regexp='💱Курсы валют')
async def show_currency(msg: types.Message):
    await msg.reply(currency_foreign(), reply_markup=KeyboardHandler.kb_client)


@dp.message_handler(regexp='⏪Назад')
async def step_back(msg: types.Message):
    await msg.reply('Переходим в прошлое меню', reply_markup=params['back'])


@dp.message_handler(regexp='☠Отменить')
async def step_back(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.reply('Отменяем...', reply_markup=KeyboardHandler.kb_client)


@dp.message_handler()
@check_words
async def echo_send(msg: types.Message, *args, **kwargs):
    await msg.answer(msg.text)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)