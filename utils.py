from aiogram.dispatcher import FSMContext
from time import sleep
import constants, string
from random import choice
from aiogram import types

import googlemaps
from datetime import datetime


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



