from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from main_keyboard import KeyboardHandler
from .weather_utils import WeatherHandler, weather, weather_forecast
from create_bot import *
from .weather_keyboard import *

weather_params = WeatherHandler()

async def get_simple_weather(msg: types.Message):
    await bot.send_message(msg.from_user.id, weather(weather_params),
                           reply_markup=KeyboardHandler.main_kb)


async def get_full_weather(msg: types.Message):
    await bot.send_message(msg.from_user.id, weather(weather_params, True),
                           reply_markup=KeyboardHandler.main_kb)


async def get_weather(msg: types.Message):
    history.put(KeyboardHandler.main_kb)
    await bot.send_message(msg.from_user.id, 'Выберите расположение', reply_markup=location_client)


async def get_weather_current(msg: types.Message):
    history.put(weather_prognosus)
    await bot.send_message(msg.from_user.id, weather(weather_params, True),
                           reply_markup=KeyboardHandler.main_kb)


async def get_prognosus(msg: types.Message):
    await bot.send_message(msg.from_user.id, f'Прогноз погоды для {weather_params.city}',
                           reply_markup=KeyboardHandler.main_kb)
    for item in weather_forecast(weather_params):
        await bot.send_message(msg.from_user.id, item)


async def handle_kiev(message: types.Message):
    weather_params.city = 'Kiev'
    weather_params.lat = None
    await message.answer('Выберите тип погоды', reply_markup=weather_prognosus)


async def handle_loc(message: types.Message):
    await FSMStates.city.set()
    await message.reply('Введите город')


async def input_city(msg: types.Message, state: FSMContext):
    weather_params.lat = None
    async with state.proxy() as data:
        data['city'] = msg.text
        weather_params.city = data['city']
        await msg.answer('Выберите тип погоды', reply_markup=weather_prognosus)
    await state.finish()


async def handle_location(message: types.Message):
    weather_params.lat = message.location.latitude
    weather_params.lon = message.location.longitude
    await message.answer('Выберите тип погоды', reply_markup=weather_prognosus)


def register_handlers_weather(dp: Dispatcher):
    dp.register_message_handler(get_simple_weather, Text('🌡Температура воздуха'))
    dp.register_message_handler(get_full_weather, Text('☔🌢🌅Полная информация'))
    dp.register_message_handler(get_weather, Text('☀Погода'))
    dp.register_message_handler(get_weather_current, Text('⌚Текущая'))
    dp.register_message_handler(get_prognosus, Text('👀Прогноз погоды'))
    dp.register_message_handler(handle_kiev, Text('🌃Киев'))
    dp.register_message_handler(handle_loc, Text('🏞Выберите населенный пункт'))
    dp.register_message_handler(input_city, state=FSMStates.city)
    dp.register_message_handler(handle_location, content_types=['location'])

