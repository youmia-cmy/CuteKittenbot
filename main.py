import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
import aiohttp

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN 未设置！请在 Railway 添加")

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人启动成功！")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>可用命令：</b>\n"
        "/start\n"
        "/help\n"
        "/token <合约地址>   ← 注意要有空格！"
    )

@dp.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ 用法：/token 0x合约地址\n注意空格")
        return

    address = parts[1].strip()
    await message.answer("🔍 正在查询...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}") as resp:
                data = await resp.json()
                if not data.get("pairs"):
                    await message.answer("未找到交易对")
                    return
                pair = data["pairs"][0]
                text = f"🪙 <b>{pair['baseToken']['name']}</b> ({pair['baseToken']['symbol']})\n💰 价格: ${pair.get('priceUsd', 'N/A')}"
                await message.answer(text)
        except Exception:
            await message.answer("查询失败，请检查合约地址")

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 机器人启动中...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
