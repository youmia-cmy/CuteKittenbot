import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN 环境变量未设置！")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ====================== 基础命令 ======================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "😺 喵～ 我是 Cute Kitten 机器人！\n\n"
        "目前支持的命令：\n"
        "/help - 查看帮助\n"
        "/game - 小游戏\n"
        "/token - 查询代币\n"
        "/lottery - 抽奖\n"
        "欢迎新成员功能已开启～"
    )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 可用命令列表：\n\n"
        "/start - 启动机器人\n"
        "/help - 显示此帮助\n"
        "/mute - 全体禁言（仅管理员）\n"
        "/unmute - 解除禁言（仅管理员）\n"
        "/token <合约地址> - 查询代币信息\n"
        "/game - 进入游戏菜单\n"
        "/lottery - 启动抽奖\n\n"
        "违禁词自动踢人功能已启用。"
    )

# ====================== 启动 ======================
async def main():
    # 删除旧 webhook，强制使用 polling
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ Webhook 已删除，开始 Polling...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
