import asyncio
import logging
import os
import random
from datetime import timedelta

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
import aiohttp

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "0").split(",") if x.strip()]

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ====================== 管理员检查 ======================
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# ====================== 基础命令 ======================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人启动成功！\n发送 /help 查看所有命令")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>可用命令列表：</b>\n\n"
        "/start - 启动机器人\n"
        "/help - 显示帮助\n"
        "/token <合约地址> - 查询代币详情\n"
        "/game - 小游戏菜单\n"
        "/lottery - 启动抽奖\n"
        "/mute - 全体禁言（仅管理员）\n"
        "/unmute - 解除全体禁言（仅管理员）\n"
        "/kick - 移除用户（回复消息使用，仅管理员）\n"
        "/ban - 封禁用户（回复消息使用，仅管理员）\n"
        "/addword - 添加违禁关键词（仅管理员）\n"
        "/delword - 删除违禁关键词（仅管理员）\n"
        "/settings - 机器人设置（仅管理员）"
    )

# ====================== 代币查询 ======================
@dp.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ 用法：/token 0x合约地址\n注意 /token 后面要加空格")
        return

    address = parts[1].strip()
    await message.answer("🔍 正在查询代币信息，请稍等...")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}") as resp:
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
            await message.answer(f"❌ 查询失败: {str(e)[:150]}")

# ====================== 小游戏 ======================
@dp.message(Command("game"))
async def cmd_game(message: Message):
    await message.answer("🎮 小游戏菜单（开发中）\n\n目前支持：\n• 猜数字（待完善）\n• 石头剪刀布（待完善）")

# ====================== 抽奖 ======================
@dp.message(Command("lottery"))
async def cmd_lottery(message: Message):
    await message.answer("🎟️ 抽奖功能开发中...\n目前支持格式：/lottery 人数 奖品名称")

# ====================== 管理命令 ======================
@dp.message(Command("mute"))
async def cmd_mute(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ 此命令仅管理员可用")
        return
    await message.answer("✅ 已全体禁言（功能待完善，当前仅提示）")

@dp.message(Command("unmute"))
async def cmd_unmute(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ 此命令仅管理员可用")
        return
    await message.answer("✅ 已解除全体禁言（功能待完善）")

@dp.message(Command("kick"))
async def cmd_kick(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ 此命令仅管理员可用")
        return
    if not message.reply_to_message:
        await message.answer("请回复要踢出的用户消息")
        return
    await message.answer("👢 已移除用户（功能待完善）")

@dp.message(Command("ban"))
async def cmd_ban(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ 此命令仅管理员可用")
        return
    if not message.reply_to_message:
        await message.answer("请回复要封禁的用户消息")
        return
    await message.answer("🚫 已封禁用户（功能待完善）")

# ====================== 启动 ======================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info(f"🚀 Cute Kitten 机器人启动成功 | 管理员数量: {len(ADMIN_IDS)}")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
