import typing
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from main_keyboard import KeyboardHandler
from .weather_utils import WeatherHandler, weather, weather_forecast, get_location
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
                           reply_markup=KeyboardHandler.main_kb, parse_mode='HTML')


async def get_prognosus(msg: types.Message):
    await bot.send_message(msg.from_user.id, f'Прогноз погоды для {weather_params.city}',
                           reply_markup=KeyboardHandler.main_kb)
    for item in weather_forecast(weather_params):
        await bot.send_message(msg.from_user.id, item, parse_mode='HTML', reply_markup=location_client)


async def handle_kiev(message: types.Message):
    history.put(location_client)
    weather_params.city = 'Kiev'
    weather_params.lat = None
    await message.answer('Выберите тип погоды', reply_markup=weather_prognosus)


async def handle_loc(message: types.Message):
    history.put(location_client)
    await FSMStates.city.set()
    await message.reply('Введите город')


async def input_city(msg: types.Message, state: FSMContext):
    weather_params.lat = None
    async with state.proxy() as data:
        data['city'] = msg.text
        weather_params.city = data['city']
        if not get_location(weather_params):
            await msg.answer('Данный город не обнаружен, попробуйте еще раз', reply_markup=history.get())
        else:
            await msg.answer('Выберите тип погоды', reply_markup=weather_prognosus)
    await state.finish()


async def handle_location(message: types.Message):
    history.put(location_client)
    weather_params.lat = message.location.latitude
    weather_params.lon = message.location.longitude
    await message.answer('Выберите тип погоды', reply_markup=weather_prognosus)


async def set_inline_prognosus(message: types.Message):
    await bot.send_message(message.from_user.id, '************ Выберите период ***************',
                           reply_markup=period_kb)


async def select_prognosus(callback: types.CallbackQuery, callback_data: typing.Dict[str, str]):
    await callback.answer()
    answer = callback_data['data']
    await bot.send_message(callback.from_user.id, f'<h2>Прогноз погоды для {weather_params.city}</h2>',
                           reply_markup=KeyboardHandler.main_kb, parse_mode='HTML')
    if answer in ('0', '1'):
        out = weather_forecast(weather_params)[int(answer)]
    else:
        out = '\n\n'.join(weather_forecast(weather_params)[0:int(answer)])
    await bot.send_message(callback.from_user.id, out, parse_mode='HTML')


def register_handlers_weather(dp: Dispatcher):
    dp.register_message_handler(get_simple_weather, Text('🌡Температура воздуха'))
    dp.register_message_handler(get_full_weather, Text('☔🌢🌅Полная информация'))
    dp.register_message_handler(get_weather, Text('☀Погода'))
    dp.register_message_handler(get_weather_current, Text('⌚Текущая'))
    dp.register_message_handler(set_inline_prognosus, Text('👀Прогноз погоды'))
    dp.register_callback_query_handler(select_prognosus, period_data.filter(data=['0', '1', '3', '5', '7']))
    dp.register_message_handler(handle_kiev, Text('🌃Киев'))
    dp.register_message_handler(handle_loc, Text('🏞Выберите населенный пункт'))
    dp.register_message_handler(input_city, state=FSMStates.city)
    dp.register_message_handler(handle_location, content_types=['location'])

