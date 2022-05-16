from aiogram.dispatcher import FSMContext
from time import sleep
import config, string
from random import choice
from aiogram import types


def check_words(fn):
    async def inner(msg: types.Message, state: FSMContext, *args, **kwargs):
        if any(word in msg.text.lower().
                translate(str.maketrans('', '', string.punctuation)) for word in config.BAD_WORDS):
            await msg.reply(choice(config.ANSWER_FOR_BAD_WORDS))
            await state.finish()
            sleep(3)
            await msg.delete()
        else:
            await fn(msg, state, *args, **kwargs)
    return inner



