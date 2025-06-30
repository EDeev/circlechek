import asyncio, logging, warnings

from init import *
from handlers import router


async def main() -> None:
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skipUpdates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # warnings.filterwarnings("ignore")

    try: asyncio.run(main())
    except KeyboardInterrupt: pass
