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

YOUR_X_USERNAME = "_StarryMiu"
YOUR_WEBSITE = "https://cutekitten.hair/"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ====================== 主菜单（简化文字匹配） ======================
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="查询代币"), KeyboardButton(text="小游戏")],
            [KeyboardButton(text="抽奖"), KeyboardButton(text="我的 X 主页")],
            [KeyboardButton(text="设置"), KeyboardButton(text="帮助")]
        ],
        resize_keyboard=True
    )

# ====================== 石头剪刀布键盘 ======================
def get_rps_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="石头"), KeyboardButton(text="剪刀"), KeyboardButton(text="布")]
        ],
        resize_keyboard=True
    )

# ====================== 基础命令 ======================
@dp.message(Command("start", "menu"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人启动成功！\n请点击下方按钮使用功能", reply_markup=get_main_menu())

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("发送 /menu 打开主菜单即可使用所有功能～", reply_markup=get_main_menu())

@dp.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 你的用户 ID 是：\n<code>{message.from_user.id}</code>", parse_mode="HTML")

# ====================== 按钮处理（使用更宽松的匹配） ======================
@dp.message(lambda m: "查询代币" in m.text)
async def menu_token(message: Message):
    await message.answer("请发送：/token 0x合约地址 （注意空格）")

@dp.message(lambda m: "小游戏" in m.text)
async def menu_game(message: Message):
    await message.answer("🎮 小游戏菜单\n目前支持石头剪刀布", reply_markup=get_rps_keyboard())

@dp.message(lambda m: "抽奖" in m.text)
async def menu_lottery(message: Message):
    await message.answer("🎟️ 抽奖功能开发中...\n示例：/lottery 10 奖品名称")

@dp.message(lambda m: "我的 X 主页" in m.text)
async def menu_x_profile(message: Message):
    text = f"""🐦 **我的 X 主页**
https://x.com/{YOUR_X_USERNAME}

🌐 **我的网站**
{YOUR_WEBSITE}"""
    await message.answer(text)

@dp.message(lambda m: "设置" in m.text)
async def menu_settings(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("⚙️ 管理员设置菜单\n可用：/mute /unmute /kick")
    else:
        await message.answer("⚙️ 设置菜单\n普通用户暂无权限～")

@dp.message(lambda m: "帮助" in m.text)
async def menu_help(message: Message):
    await cmd_help(message)

# ====================== 石头剪刀布 ======================
@dp.message(lambda m: m.text in ["石头", "剪刀", "布"])
async def play_rps(message: Message):
    user = message.text
    bot_choice = random.choice(["石头", "剪刀", "布"])
    if user == bot_choice:
        result = "🤝 平局！"
    elif (user == "石头" and bot_choice == "剪刀") or (user == "剪刀" and bot_choice == "布") or (user == "布" and bot_choice == "石头"):
        result = "🎉 你赢了！"
    else:
        result = "😿 你输了～"
    await message.answer(f"你出：{user}\n我出：{bot_choice}\n\n{result}", reply_markup=get_rps_keyboard())

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
            await message.answer("查询失败")

# ====================== 启动 ======================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Cute Kitten 机器人启动成功！")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
