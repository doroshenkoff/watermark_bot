import logging, os, string, json, constants
from utils import weather, weather_forecast
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from random import choice
from time import sleep
from utils import WeatherHandler, currency_foreign
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboard import KeyboardHandler
from inline_keyboard import InlineKeyboardHandler
from datetime import datetime
from watermark import create_watermark
from queue import LifoQueue

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(os.getenv('TOKEN_TELEGRAM'))

dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

weather_params = WeatherHandler()

params = {
    'vote_up': 0,
    'vote_down': 0
}

history = LifoQueue()


def clear_history():
    global history
    history = LifoQueue()


class FSMStates(StatesGroup):
    city = State()
    image_for_watermark = State()
    watermark_word = State()


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
                           reply_markup=KeyboardHandler.kb_client)


@dp.message_handler(Text('🌡Температура воздуха'))
async def get_simple_weather(msg: types.Message):
    clear_history()
    await bot.send_message(msg.from_user.id, weather(weather_params),
                           reply_markup=KeyboardHandler.kb_client)


@dp.message_handler(Text('☔🌢🌅Полная информация'))
async def get_full_weather(msg: types.Message):
    clear_history()
    await bot.send_message(msg.from_user.id, weather(weather_params, True),
                           reply_markup=KeyboardHandler.kb_client)


@dp.message_handler(Text('☀Погода'))
async def get_weather(msg: types.Message):
    history.put(KeyboardHandler.kb_client)
    await bot.send_message(msg.from_user.id, 'Выберите расположение', reply_markup=KeyboardHandler.location_client)


# 'Выберите тип погоды', reply_markup=KeyboardHandler.weather_prognosus

@dp.message_handler(Text('⌚Текущая'))
async def get_weather_current(msg: types.Message):
    history.put(KeyboardHandler.weather_prognosus)
    await bot.send_message(msg.from_user.id, weather(weather_params, True),
                           reply_markup=KeyboardHandler.kb_client)


@dp.message_handler(Text('👀Прогноз погоды'))
async def get_prognosus(msg: types.Message):
    await bot.send_message(msg.from_user.id, f'Прогноз погоды для {weather_params.city}',
                           reply_markup=KeyboardHandler.kb_client)
    for item in weather_forecast(weather_params):
        await bot.send_message(msg.from_user.id, item)



@dp.message_handler(Text('🌃Киев'))
async def handle_kiev(message: types.Message):
    weather_params.city = 'Kiev'
    weather_params.lat = None
    await message.answer('Выберите тип погоды', reply_markup=KeyboardHandler.weather_prognosus)


@dp.message_handler(Text('🏞Выберите населенный пункт'))
async def handle_loc(message: types.Message):
    await FSMStates.city.set()
    await message.reply('Введите город')


@dp.message_handler(state=FSMStates.city)
async def input_city(msg: types.Message, state: FSMContext):
    weather_params.lat = None
    async with state.proxy() as data:
        data['city'] = msg.text
        weather_params.city = data['city']
        await msg.answer('Выберите тип погоды', reply_markup=KeyboardHandler.weather_prognosus)
    await state.finish()


#     **********************************************
@dp.message_handler(Text('💧Нанести водяной знак'))
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
        await msg.reply('Теперь введите текст для водяного знака (не больше 20 символов',
                        reply_markup=KeyboardHandler.undo_client)


@dp.message_handler(state=FSMStates.watermark_word)
@check_words
async def input_text(msg: types.Message, state: FSMContext, *args, **kwargs):
    async with state.proxy() as data:
        if len(msg.text) > 20:
            await msg.reply('Длина строки больше 20 символов, введти другой текст')
            await FSMStates.watermark_word.state
        elif msg.text == '☠Отменить':
            await state.finish()
            await msg.reply('Отменяем...', reply_markup=KeyboardHandler.kb_client)
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
    await message.answer('Выберите тип погоды', reply_markup=KeyboardHandler.weather_prognosus)


@dp.message_handler(Text('💱Курсы валют'))
async def show_currency(msg: types.Message):
    await msg.reply(currency_foreign(), reply_markup=KeyboardHandler.kb_client)


@dp.message_handler(Text('⏪Назад'))
async def step_back(msg: types.Message):
    await msg.reply('Переходим в прошлое меню', reply_markup=history.get())


@dp.message_handler(Text('Inline button test'))
async def inline_test(msg: types.Message):
    message = f'👍 - {params["vote_up"]}, 👎 - {params["vote_down"]}'
    await msg.reply('Для отмены выберите пункт меню Отменить', reply_markup=KeyboardHandler.undo_client)
    inline_msg = await bot.send_message(msg.from_user.id, message, reply_markup=InlineKeyboardHandler.vote_ikb)
    params['msg_id'] = inline_msg.message_id


@dp.message_handler(state='*', regexp='☠Отменить')
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
    await msg.reply('Отменяем...', reply_markup=KeyboardHandler.kb_client)


@dp.callback_query_handler(lambda msg: msg.data in ['like', 'dislike'])
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


@dp.message_handler()
@check_words
async def echo_send(msg: types.Message, *args, **kwargs):
    await msg.answer(msg.text)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)