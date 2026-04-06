import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import aiohttp

# 配置
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN 未设置！请检查 Railway 变量")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ==================== 命令处理 ====================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人启动成功！\n\n试试发送 /help")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>可用命令：</b>\n"
        "/start - 启动机器人\n"
        "/help - 显示帮助\n"
        "/token <合约地址> - 查询代币（注意空格）\n"
        "/game - 小游戏（待加）\n"
        "/lottery - 抽奖（待加）"
    )

@dp.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ 用法错误！\n正确格式必须有空格：\n/token 0x你的合约地址")
        return

    address = parts[1].strip()
    await message.answer("🔍 正在从 DexScreener 查询，请稍等...")

    async with aiohttp.ClientSession() as session:
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
            async with session.get(url) as resp:
                if resp.status != 200:
                    await message.answer("❌ 查询失败，请检查合约地址")
                    return
                data = await resp.json()

            if not data.get("pairs"):
                await message.answer("❌ 未找到该合约的交易对")
                return

            pair = data["pairs"][0]
            text = f"""🪙 <b>{pair['baseToken']['name']}</b> ({pair['baseToken']['symbol']})

💰 价格: ${pair.get('priceUsd', 'N/A')}
💧 流动性: ${pair['liquidity']['usd']:,.0f}
📊 市值: ${pair.get('fdv', 'N/A'):,.0f}
🔗 链: {pair['chainId'].upper()}"""

            await message.answer(text)
        except Exception as e:
            await message.answer(f"❌ 查询出错: {str(e)[:150]}")

# ==================== 启动 ====================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Cute Kitten 机器人正在启动...")

    # 强制删除旧 webhook，防止冲突
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ 已删除旧 webhook，切换到 Polling 模式")

    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
