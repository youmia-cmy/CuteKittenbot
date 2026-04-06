import asyncio
import logging
import os
import random
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ====================== 主菜单 ======================
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 查询代币"), KeyboardButton(text="🎮 小游戏")],
            [KeyboardButton(text="🎟️ 抽奖"), KeyboardButton(text="⚙️ 设置")],
            [KeyboardButton(text="📋 帮助"), KeyboardButton(text="🆔 我的ID")]
        ],
        resize_keyboard=True
    )

# ====================== 石头剪刀布键盘 ======================
def get_rps_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✊ 石头"), KeyboardButton(text="✌️ 剪刀"), KeyboardButton(text="✋ 布")]
        ],
        resize_keyboard=True
    )

# ====================== 命令 ======================
@dp.message(Command("start", "menu"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人启动成功！\n点击下方按钮使用功能～", reply_markup=get_main_menu())

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("📋 发送 /menu 打开主菜单即可使用所有功能～")

@dp.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 你的用户 ID 是：\n<code>{message.from_user.id}</code>", parse_mode="HTML")

# ====================== 菜单按钮处理 ======================
@dp.message(lambda m: m.text == "🔍 查询代币")
async def menu_token(message: Message):
    await message.answer("请发送：/token 0x合约地址 （注意空格）")

@dp.message(lambda m: m.text == "🎮 小游戏")
async def menu_game(message: Message):
    await message.answer(
        "🎮 **小游戏菜单**\n\n"
        "目前支持：\n"
        "• 石头剪刀布（已可用）\n"
        "• 猜数字（后续添加）",
        reply_markup=get_rps_keyboard()
    )

@dp.message(lambda m: m.text in ["✊ 石头", "✌️ 剪刀", "✋ 布"])
async def play_rps(message: Message):
    user_choice = message.text
    bot_choice = random.choice(["✊ 石头", "✌️ 剪刀", "✋ 布"])

    # 判断胜负
    if user_choice == bot_choice:
        result = "🤝 平局！"
    elif (user_choice == "✊ 石头" and bot_choice == "✌️ 剪刀") or \
         (user_choice == "✌️ 剪刀" and bot_choice == "✋ 布") or \
         (user_choice == "✋ 布" and bot_choice == "✊ 石头"):
        result = "🎉 你赢了！"
    else:
        result = "😿 你输了～"

    await message.answer(
        f"你出：{user_choice}\n"
        f"我出：{bot_choice}\n\n"
        f"{result}\n\n"
        "再来一局吗？继续点击按钮即可～",
        reply_markup=get_rps_keyboard()
    )

@dp.message(lambda m: m.text == "🎟️ 抽奖")
async def menu_lottery(message: Message):
    await message.answer("🎟️ 抽奖功能开发中...\n示例：/lottery 10 奖品名称")

@dp.message(lambda m: m.text == "⚙️ 设置")
async def menu_settings(message: Message):
    await message.answer("⚙️ 设置菜单开发中...（管理员可用）")

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
    logging.info("🚀 Cute Kitten 机器人启动成功！")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
