import logging, json, argparse, asyncio
from aiogram import types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from create_bot import *
from main_keyboard import KeyboardHandler
from weather.weather_handler import register_handlers_weather
from finance.finance_handler import register_handlers_finance
from weather.weather_utils import is_rain
from watermark.watermark_handler import register_handlers_watermark
from utils import check_words
from config import WEBHOOK_URL, WEBAPP_PORT, production
from astrology.astro_utils import get_horoscope, is_via_combusta
from datetime import datetime
from finance.finance_handler import currency_foreign

logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())


async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    history.put(KeyboardHandler.main_kb)
    try:
        with open('static/params.json') as f:
            start_up_params = json.load(f)
    except:
        pass


async def write_changes():
    try:
        with open('static/params.json', 'w') as f:
            json.dump(params, f)
    except:
        pass


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


async def send_quotations():
    while params.get('flag'):
        await asyncio.sleep(60)
        now = datetime.now()
        if now.hour in range(8, 24, 2) and now.minute == 0:
            await bot.send_message(params['chat_id'], f'<b>Биржевые котировки на {now.hour}:00</b>', parse_mode='HTML')
            await bot.send_message(params['chat_id'], currency_foreign())
        if now.hour in range(5, 24, 2):
            rain_msg = is_rain()
            if rain_msg:
                await bot.send_message(params['chat_id'], rain_msg)
        if now.minute == 0:
            if is_via_combusta() and not params.get('via_combusta'):
                await bot.send_message(params['chat_id'], '⚠Attention! The Moon has entered VIA COMBUSTA!💀')
                params['via_combusta'] = True
            elif not is_via_combusta() and params.get('via_combusta'):
                await bot.send_message(params['chat_id'], '🌙The Moon has exited via combusta!😇')
                params['via_combusta'] = False


async def start_cmd(msg: types.Message):
    params['chat_id'] = msg.from_user.id
    params['flag'] = True
    params['flag1'] = True
    await bot.send_message(msg.from_user.id, 'Выберите что-то из пункта меню',
                           reply_markup=KeyboardHandler.main_kb)
    await send_quotations()



async def stop_schedule(msg: types.Message):
    if not params['flag']:
        params['flag1'] = False
    else:
        params['flag'] = False
    await msg.answer('Прекращаем спамить...')



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
    dp.register_message_handler(stop_schedule, commands=['stop'])
    dp.register_message_handler(step_back, Text('⏪Назад'))
    dp.register_message_handler(horoscope, Text('🌎Положение планет'))
    dp.register_message_handler(echo_send)
    dp.register_message_handler(cancel_handler, Text('☠Отменить'), state='*')


async def on_shutdown(dp):
    logging.warning('Shutting down..')
    await write_changes()
    await bot.delete_webhook()

    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')



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


