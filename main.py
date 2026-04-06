import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import aiohttp

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN 未设置！请在 Railway 变量中添加")

BOT = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# ====================== 命令 ======================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人已通过 Webhook 启动成功！\n发送 /help 查看命令")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>可用命令：</b>\n"
        "/start - 启动\n"
        "/help - 帮助\n"
        "/token <合约地址> - 查询代币\n"
        "/game - 小游戏（待完善）\n"
        "/lottery - 抽奖（待完善）"
    )

@dp.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("用法：/token <合约地址>\n例如：/token 0x...")
        return
    address = parts[1].strip()
    await message.answer("🔍 正在查询，请稍等...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}") as resp:
                data = await resp.json()
                if not data.get("pairs"):
                    await message.answer("未找到交易对")
                    return
                pair = data["pairs"][0]
                await message.answer(
                    f"🪙 <b>{pair['baseToken']['name']}</b> ({pair['baseToken']['symbol']})\n"
                    f"价格: ${pair.get('priceUsd', 'N/A')}\n"
                    f"流动性: ${pair['liquidity']['usd']:,.0f}"
                )
        except Exception as e:
            await message.answer(f"查询失败: {str(e)[:100]}")

# ====================== Webhook 设置 ======================
async def on_startup(bot: Bot):
    webhook_url = os.getenv("WEBHOOK_URL")  # Railway 会自动提供域名
    if webhook_url:
        await bot.set_webhook(f"{webhook_url}/webhook")
        logging.info(f"✅ Webhook 已设置: {webhook_url}/webhook")
    else:
        logging.warning("⚠️ WEBHOOK_URL 未设置，将使用 polling")

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Cute Kitten 机器人启动中...")

    # 启动 webhook
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=BOT).register(app, path="/webhook")
    setup_application(app, dp, bot=BOT)

    runner = web.AppRunner(app)
    await runner.setup()

    # Railway 提供的端口
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    logging.info(f"✅ Webhook 服务已在端口 {port} 启动")
    await asyncio.Event().wait()  # 保持运行

if __name__ == "__main__":
    asyncio.run(main())
