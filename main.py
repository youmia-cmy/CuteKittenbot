import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
import aiohttp

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

logging.info(f"🚀 启动成功 | 当前管理员 ID: {ADMIN_IDS}")

# ====================== 管理员检查 ======================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ====================== 命令 ======================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(f"😺 喵～ 启动成功！\n你的用户ID: <code>{message.from_user.id}</code>", parse_mode="HTML")

@dp.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 你的用户 ID 是：\n<code>{message.from_user.id}</code>\n\n请把这个数字添加到 Railway 的 ADMIN_IDS 变量中", parse_mode="HTML")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>可用命令：</b>\n\n"
        "/start - 启动机器人\n"
        "/myid - 显示你的用户ID\n"
        "/help - 显示帮助\n"
        "/token <合约地址> - 查询代币\n"
        "/mute - 全体禁言（仅管理员）\n"
        "/unmute - 解除禁言（仅管理员）"
    )

@dp.message(Command("mute"))
async def cmd_mute(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(f"❌ 仅管理员可用\n你的ID: {message.from_user.id}\n管理员列表: {ADMIN_IDS}")
        return
    await message.answer("✅ 已执行全体禁言（当前为提示模式）")

@dp.message(Command("unmute"))
async def cmd_unmute(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(f"❌ 仅管理员可用\n你的ID: {message.from_user.id}")
        return
    await message.answer("✅ 已解除全体禁言（当前为提示模式）")

# 代币查询保持可用
@dp.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ 用法：/token 0x合约地址 （注意空格）")
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
            await message.answer("查询失败")

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
