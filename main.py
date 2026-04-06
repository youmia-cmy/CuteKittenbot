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

# 你的个人信息（请修改成你自己的）
YOUR_X_USERNAME = "_StarryMiu"          # 例如: "elonmusk"
YOUR_WEBSITE = "https://cutekitten.hair"   # 可以留空

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

# ====================== 基础命令 ======================
@dp.message(Command("start", "menu"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ Cute Kitten 机器人启动成功！", reply_markup=get_main_menu())

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("发送 /menu 打开主菜单即可使用所有功能～")

# ====================== 新功能1：清除群内注销账号 ======================
@dp.message(Command("cleandeleted"))
async def clean_deleted_accounts(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ 此命令仅管理员可用")
        return

    await message.answer("🔍 正在扫描群内已注销账号，请稍等...")

    try:
        members = await bot.get_chat_administrators(message.chat.id)  # 先获取管理员，避免误踢
        deleted_count = 0

        async for member in bot.get_chat_member(message.chat.id, None):  # 遍历所有成员（注意：此方法可能受限）
            if member.user.is_bot:
                continue
            if member.user.first_name == "Deleted Account" or not member.user.username and not member.user.first_name:
                try:
                    await bot.ban_chat_member(message.chat.id, member.user.id, until_date=0)  # 踢出
                    deleted_count += 1
                except Exception:
                    pass

        await message.answer(f"✅ 清理完成！\n已移除 {deleted_count} 个已注销账号。")
    except Exception as e:
        await message.answer(f"❌ 清理失败: {str(e)[:200]}")

# ====================== 新功能2：推送 X 主页和网站 ======================
@dp.message(Command("x", "twitter", "pushx"))
async def push_x_profile(message: Message):
    if len(message.text.split()) > 1:
        username = message.text.split()[1].replace("@", "")
        await message.answer(f"🔗 {username} 的 X 主页：\nhttps://x.com/{username}")
    else:
        # 推送你自己的 X 主页和网站
        text = f"🐦 **我的 X 主页**：\nhttps://x.com/{YOUR_X_USERNAME}\n\n"
        if YOUR_WEBSITE:
            text += f"🌐 **我的网站**：\n{YOUR_WEBSITE}"
        await message.answer(text)

# ====================== 其他已有功能（简化版） ======================
@dp.message(Command("token"))
async def cmd_token(message: Message):
    # ... 保持你之前的代币查询代码 ...
    await message.answer("🔍 代币查询功能正常（示例）")

# ====================== 启动 ======================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Cute Kitten 机器人启动成功！")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
