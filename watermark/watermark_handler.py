from aiogram.dispatcher.filters import Text
from aiogram import types
from main_keyboard import KeyboardHandler
from aiogram.dispatcher import FSMContext
from datetime import datetime
from utils import check_words
from .watermark import create_watermark
from create_bot import *


async def make_watermark(msg: types.Message):
    await FSMStates.image_for_watermark.set()
    await msg.reply('Выберите картинку', reply_markup=KeyboardHandler.undo_kb)


async def input_photo(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        now = datetime.now()
        name = f'static/photos/img-{now.year}-{now.month}-{now.day}--{now.hour}-{now.minute}.jpg'
        try:
            await msg.photo[-1].download(name)
        except:
            await msg.reply('Данная операция невозможна, идите нахуй...',
                            reply_markup=KeyboardHandler.undo_kb)
        data['image_for_watermark'] = name
        await FSMStates.next()
        await msg.reply('Теперь введите текст для водяного знака (не больше 20 символов',
                        reply_markup=KeyboardHandler.undo_kb)


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


def register_handlers_watermark(dp: Dispatcher):
    dp.register_message_handler(make_watermark, Text('💧Нанести водяной знак'))
    dp.register_message_handler(input_photo, content_types=['photo'], state=FSMStates.image_for_watermark)
    dp.register_message_handler(input_text, state=FSMStates.watermark_word)