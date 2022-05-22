import logging, json, argparse, schedule
from aiogram import types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from create_bot import *
from main_keyboard import KeyboardHandler
from weather.weather_handler import register_handlers_weather
from finance.finance_handler import register_handlers_finance
from watermark.watermark_handler import register_handlers_watermark
from utils import check_words
from config import WEBHOOK_URL, WEBAPP_PORT, production
from astrology.astro_utils import get_horoscope

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    history.put(KeyboardHandler.main_kb)
    try:
        with open('static/params.json') as f:
            start_up_params = json.load(f)
            params['vote_up'] = start_up_params['vote_up']
            params['vote_down'] = start_up_params['vote_down']
    except:
        params['vote_up'] = 0
        params['vote_down'] = 0


async def write_changes():
    try:
        with open('static/params.json', 'w') as f:
            json.dump(params, f)
    except:
        pass


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await write_changes()
    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')


async def start_cmd(msg: types.Message):
    params['chat_id'] = msg.from_user.id
    schedule.every(30).seconds.do(send_greeting)
    await bot.send_message(msg.from_user.id, 'Выберите что-то из пункта меню',
                           reply_markup=KeyboardHandler.main_kb)


async def step_back(msg: types.Message):
    print(history)
    await msg.reply('Переходим в прошлое меню', reply_markup=history.get())


async def cancel_handler(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if params.get('msg_id'):
        try:
            await bot.delete_message(msg.from_user.id, params['msg_id'])
        except:
            pass
    await write_changes()
    if current_state:
        await state.finish()
    await msg.reply('Отменяем...', reply_markup=KeyboardHandler.main_kb)


async def send_greeting():
    if params.get('chat_id'):
        await bot.send_message(params['chat_id'], 'Hello, <i>Pidar</i>', parse_mode='HTML')


async def horoscope(msg: types.Message):
    await msg.answer(get_horoscope(), reply_markup=KeyboardHandler.main_kb, parse_mode='HTML')


@check_words
async def echo_send(msg: types.Message, *args, **kwargs):
    await msg.answer(msg.text)


def register_handlers(dp: Dispatcher):
    register_handlers_weather(dp)
    register_handlers_finance(dp)
    register_handlers_watermark(dp)
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_message_handler(step_back, Text('⏪Назад'))
    dp.register_message_handler(horoscope, Text('🌎Положение планет'))
    dp.register_message_handler(echo_send)
    dp.register_message_handler(cancel_handler, Text('☠Отменить'), state='*')


def main(production=True):
    register_handlers(dp)
    if production:
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            skip_updates=True,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
    else:
        executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--p', help='Turns on production mode')
    args = parser.parse_args()
    if args.p:
        production = True
    main(production)
