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
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()]

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

logging.info(f"当前管理员 ID 列表: {ADMIN_IDS}")

# ====================== 管理员检查 ======================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ====================== 基础命令 ======================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(f"😺 喵～ 机器人启动成功！\n你的ID: {message.from_user.id}\n管理员列表: {ADMIN_IDS}")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>可用命令：</b>\n\n"
        "/start - 启动机器人\n"
        "/help - 显示帮助\n"
        "/token <合约地址> - 查询代币\n"
        "/mute - 全体禁言（仅管理员）\n"
        "/unmute - 解除禁言（仅管理员）\n"
        "/kick - 移除用户（回复消息）\n"
        "/ban - 封禁用户（回复消息）"
    )

# ====================== 管理命令 ======================
@dp.message(Command("mute"))
async def cmd_mute(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(f"❌ 此命令仅管理员可用\n你的ID: {message.from_user.id}\n管理员ID: {ADMIN_IDS}")
        return
    await message.answer("✅ 已执行全体禁言（当前为提示模式）")

@dp.message(Command("unmute"))
async def cmd_unmute(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer(f"❌ 此命令仅管理员可用\n你的ID: {message.from_user.id}")
        return
    await message.answer("✅ 已解除全体禁言（当前为提示模式）")

@dp.message(Command("kick"))
async def cmd_kick(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ 此命令仅管理员可用")
        return
    if not message.reply_to_message:
        await message.answer("请回复要踢出的用户消息")
        return
    await message.answer("👢 已尝试移除用户（功能待完善）")

# ====================== 代币查询（保持可用） ======================
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

# ====================== 启动 ======================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info(f"🚀 机器人启动成功 | 当前管理员: {ADMIN_IDS}")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
