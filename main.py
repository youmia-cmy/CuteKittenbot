import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import aiohttp

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ====================== 主菜单键盘 ======================
def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 查询代币"), KeyboardButton(text="🎮 小游戏")],
            [KeyboardButton(text="🎟️ 抽奖"), KeyboardButton(text="⚙️ 设置")],
            [KeyboardButton(text="📋 帮助"), KeyboardButton(text="🆔 我的ID")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

# ====================== 基础命令 ======================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人启动成功！\n点击下方按钮使用功能～", reply_markup=get_main_menu())

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 <b>可用命令：</b>\n\n"
        "/start - 打开主菜单\n"
        "/help - 显示帮助\n"
        "/token <合约地址> - 查询代币\n"
        "/menu - 打开菜单\n"
        "/myid - 显示你的用户ID",
        reply_markup=get_main_menu()
    )

@dp.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer("📋 **主菜单** 请点击下方按钮操作：", reply_markup=get_main_menu())

@dp.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 你的用户 ID 是：\n<code>{message.from_user.id}</code>", parse_mode="HTML")

# ====================== 菜单按钮处理（已全部开发） ======================
@dp.message(lambda m: m.text == "🔍 查询代币")
async def menu_token(message: Message):
    await message.answer("🔍 请发送以下格式查询代币：\n/token 0x合约地址\n注意 /token 后面要加空格")

@dp.message(lambda m: m.text == "🎮 小游戏")
async def menu_game(message: Message):
    await message.answer("🎮 小游戏菜单（开发中）\n\n目前支持：\n• 猜数字\n• 石头剪刀布\n后续会陆续添加～")

@dp.message(lambda m: m.text == "🎟️ 抽奖")
async def menu_lottery(message: Message):
    await message.answer("🎟️ 抽奖功能开发中...\n\n当前支持格式示例：\n/lottery 10 奖品名称\n（例如抽10人送礼物）")

@dp.message(lambda m: m.text == "⚙️ 设置")
async def menu_settings(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("⚙️ 管理员设置菜单（开发中）\n\n可用命令：\n/mute 全体禁言\n/unmute 解除禁言\n/addword 添加违禁词")
    else:
        await message.answer("⚙️ 设置菜单\n\n普通用户暂无设置权限～")

@dp.message(lambda m: m.text == "📋 帮助")
async def menu_help(message: Message):
    await cmd_help(message)

@dp.message(lambda m: m.text == "🆔 我的ID")
async def menu_myid(message: Message):
    await cmd_myid(message)

# ====================== 代币查询 ======================
@dp.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ 用法：/token 0x合约地址 （注意空格）")
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
                text = f"🪙 <b>{pair['baseToken']['name']}</b> ({pair['baseToken']['symbol']})\n💰 价格: ${pair.get('priceUsd', 'N/A')}"
                await message.answer(text)
        except Exception:
            await message.answer("查询失败，请检查地址")

# ====================== 启动 ======================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Cute Kitten 机器人启动成功！")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
