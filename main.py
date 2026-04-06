import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logging.error("❌ BOT_TOKEN 环境变量未找到！请在 Railway 的「变量」页面添加 BOT_TOKEN")
    sys.exit(1)   # 明确退出，避免无声崩溃

logging.info(f"✅ BOT_TOKEN 已加载，长度: {len(BOT_TOKEN)}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====================== 命令 ======================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人启动成功！\n\n发送 /help 查看命令列表～")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 当前可用命令：\n"
        "/start - 启动机器人\n"
        "/help - 显示帮助\n"
        "/token <合约地址> - 查询代币\n"
        "/game - 小游戏\n"
        "/lottery - 抽奖\n\n"
        "欢迎新成员和违禁词功能正在添加中..."
    )

# ====================== 启动 ======================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Cute Kitten 机器人正在启动...")

    # 使用更安全的启动方式（先不强制 delete_webhook）
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Polling 崩溃: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
