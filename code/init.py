from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties

from config import botToken

bot = Bot(token=botToken, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


import logging, functools, sys

# logging.basicConfig(level=logging.INFO, filename='../data/info.log',filemode="w", format="%(asctime)s %(levelname)s %(message)s")

def bug_report(func):
    @functools.wraps(func)

    def wrapper(*args, **kwargs):

        try:
            result = func(*args, **kwargs)
            logging.info(f"Successful result")
            return result
        except Exception as err:
            logging.error("Ошибка", exc_info=True)
            """with open('../data/log.txt', "a") as f:
                f.write(repr(e))"""
            sys.exit()

    return wrapper

