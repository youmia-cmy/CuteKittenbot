import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN
from handlers import basic, admin, moderation, welcome, lottery, game, token_info

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# 注册所有路由
dp.include_router(welcome.welcome_router)
dp.include_router(basic.router)
dp.include_router(admin.admin_router)
dp.include_router(moderation.moder_router)
dp.include_router(token_info.token_router)
# dp.include_router(lottery.router)
# dp.include_router(game.router)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
