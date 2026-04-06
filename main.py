import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import aiohttp

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN 未设置")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ==================== 基础命令 ====================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人已启动！\n发送 /help 查看命令")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>当前可用命令：</b>\n"
        "/start - 启动机器人\n"
        "/help - 显示帮助\n"
        "/token &lt;合约地址&gt; - 查询代币详情\n"
        "/game - 小游戏（待完善）\n"
        "/lottery - 抽奖（待完善）\n\n"
        "欢迎新成员和违禁词功能正在添加中..."
    )

# ==================== 代币查询 ====================
@dp.message(Command("token"))
async def cmd_token(message: Message):
    if len(message.text.split()) < 2:
        await message.answer("用法示例：\n/token 0x1234567890abcdef1234567890abcdef12345678")
        return

    address = message.text.split()[1].strip()
    
    await message.answer("🔍 正在查询代币信息，请稍等...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}") as resp:
                if resp.status != 200:
                    await message.answer("❌ 查询失败，请检查合约地址是否正确")
                    return
                data = await resp.json()

            if not data.get("pairs"):
                await message.answer("未找到该合约的交易对")
                return

            pair = data["pairs"][0]
            info = (
                f"🪙 <b>{pair['baseToken']['name']}</b> ({pair['baseToken']['symbol']})\n\n"
                f"💰 价格: ${pair.get('priceUsd', 'N/A')}\n"
                f"💧 流动性: ${pair['liquidity']['usd']:,.0f}\n"
                f"📊 市值: ${pair.get('fdv', 'N/A'):,.0f}\n"
                f"🔗 链: {pair['chainId'].upper()}\n"
                f"🏪 DEX: {pair['dexId']}"
            )
            await message.answer(info)
        except Exception as e:
            await message.answer(f"❌ 查询出错: {str(e)[:200]}")

# ==================== 启动 ====================
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("🚀 Cute Kitten 机器人启动成功！")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
