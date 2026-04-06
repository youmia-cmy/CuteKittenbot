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

# 你的个人信息
YOUR_X_USERNAME = "StarryMiu"
YOUR_WEBSITE = "https://cutekitten.hair"

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
            [KeyboardButton(text="🎟️ 抽奖"), KeyboardButton(text="🐦 我的 X 主页")],
            [KeyboardButton(text="⚙️ 设置"), KeyboardButton(text="📋 帮助")]
        ],
        resize_keyboard=True
    )

# ====================== 管理员设置菜单 ======================
def get_admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🗑️ 清理注销账号")],
            [KeyboardButton(text="🔙 返回主菜单")]
        ],
        resize_keyboard=True
    )

# ====================== 基础命令 ======================
@dp.message(Command("start", "menu"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人启动成功！\n点击下方按钮使用功能～", reply_markup=get_main_menu())

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("发送 /menu 打开主菜单即可使用所有功能～")

@dp.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 你的用户 ID 是：\n<code>{message.from_user.id}</code>", parse_mode="HTML")

# ====================== 主菜单按钮处理 ======================
@dp.message(lambda m: m.text == "🔍 查询代币")
async def menu_token(message: Message):
    await message.answer("请发送：/token 0x合约地址 （注意空格）")

@dp.message(lambda m: m.text == "🎮 小游戏")
async def menu_game(message: Message):
    await message.answer("🎮 小游戏菜单（开发中）\n目前支持石头剪刀布")

@dp.message(lambda m: m.text == "🎟️ 抽奖")
async def menu_lottery(message: Message):
    await message.answer("🎟️ 抽奖功能开发中...\n示例：/lottery 10 奖品名称")

@dp.message(lambda m: m.text == "🐦 我的 X 主页")
async def menu_x_profile(message: Message):
    text = f"🐦 **我的 X 主页**\nhttps://x.com/{YOUR_X_USERNAME}\n\n🌐 **我的网站**\n{YOUR_WEBSITE}"
    await message.answer(text)

@dp.message(lambda m: m.text == "⚙️ 设置")
async def menu_settings(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer("⚙️ **管理员设置菜单**", reply_markup=get_admin_menu())
    else:
        await message.answer("⚙️ 设置菜单\n普通用户暂无权限～")

@dp.message(lambda m: m.text == "📋 帮助")
async def menu_help(message: Message):
    await cmd_help(message)

# ====================== 清理注销账号（改进版） ======================
@dp.message(lambda m: m.text == "🗑️ 清理注销账号")
async def menu_cleandeleted(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ 此功能仅管理员可用")
        return

    await message.answer(
        "🗑️ **清理已注销账号**\n\n"
        "机器人无法自动扫描全群。\n\n"
        "**推荐操作方式：**\n"
        "1. 在群里找到显示为 “Deleted Account” 的消息\n"
        "2. **回复那条消息**\n"
        "3. 发送 `/kick`\n\n"
        "这样就能准确踢出该已注销用户。\n\n"
        "需要清理多个时，重复以上步骤即可。"
    )

# ====================== 踢人命令（配合清理使用） ======================
@dp.message(Command("kick"))
async def cmd_kick(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ 此命令仅管理员可用")
        return

    if not message.reply_to_message:
        await message.answer("请回复要踢出的用户消息，然后再发送 /kick")
        return

    user = message.reply_to_message.from_user
    try:
        await bot.ban_chat_member(message.chat.id, user.id, until_date=30)  # 30秒后自动解封 = 踢出
        await message.answer(f"✅ 已成功踢出用户：\n{user.first_name} (ID: {user.id})")
    except Exception as e:
        await message.answer(f"❌ 踢出失败: {str(e)[:100]}")

# ====================== 启动 ======================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Cute Kitten 机器人启动成功！")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
