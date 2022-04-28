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



logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN_TELEGRAM'))

dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

weather_params = WeatherHandler()


class FSMStates(StatesGroup):
    city = State()


async def on_startup(_):
    pass


def check_words(fn):
    async def inner(msg: types.Message, *args, **kwargs):
        if any(word in msg.text.lower().
                translate(str.maketrans('', '', string.punctuation)) for word in constants.BAD_WORDS):
            await msg.reply(choice(constants.ANSWER_FOR_BAD_WORDS))
            sleep(3)
            await msg.delete()
        else:
            await fn(msg, *args, **kwargs)
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


@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    weather_params.lat = message.location.latitude
    weather_params.lon = message.location.longitude
    await message.answer('Выберите вид отображения погоды', reply_markup=KeyboardHandler.weather_client)


@dp.message_handler(regexp='💱Курсы валют')
async def show_currency(msg: types.Message):
    await msg.reply(currency_foreign(), reply_markup=KeyboardHandler.kb_client)


@dp.message_handler()
@check_words
async def echo_send(msg: types.Message, *args, **kwargs):
    await msg.answer(msg.text)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)