import logging, json, argparse, schedule
from aiogram import types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.executor import start_webhook
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from create_bot import *
from main_keyboard import KeyboardHandler
from inline_keyboard import InlineKeyboardHandler
from weather.weather_handler import register_handlers_weather
from finance.finance_handler import register_handlers_finance
from watermark.watermark_handler import register_handlers_watermark
from utils import check_words
from config import WEBHOOK_URL, WEBAPP_PORT, production

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
    await write_changes()
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
    register_handlers_watermark(dp)
    dp.register_message_handler(start_cmd, commands=['start'])
    dp.register_callback_query_handler(vote_handler, lambda msg: msg.data in ['like', 'dislike'])
    dp.register_message_handler(inline_test, Text('Inline button test'))
    dp.register_message_handler(step_back, Text('⏪Назад'))
    dp.register_message_handler(echo_send)
    dp.register_message_handler(cancel_handler, Text('☠Отменить'), state='*')


async def send_greeting():
    if params.get('chat_id'):
        await bot.send_message(params['chat_id'], 'Hello, <i>Pidar</i>', parse_mode='HTML')


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
