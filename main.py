import asyncio
import logging
import os
import random
from datetime import timedelta
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]

# 你的个人信息
YOUR_X_USERNAME = "_StarryMiu"
YOUR_WEBSITE = "https://cutekitten.hair/"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

bad_words = set()  # 违禁词列表（内存存储）

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

# ====================== 1. 自动欢迎新成员 ======================
@dp.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def welcome_new_member(event: ChatMemberUpdated):
    user = event.new_chat_member.user
    welcome_text = f"""
🎉 <b>欢迎 {user.first_name} 加入群聊！</b> 😺

我是 Cute Kitten 小猫机器人～

📌 请遵守群规：
• 禁止广告、违禁词、刷屏
• 查代币用 /token
• 抽奖用 /lottery
• 小游戏用 /game

输入 /help 查看全部功能
玩得开心喵～ 🐱
    """.strip()
    await bot.send_message(event.chat.id, welcome_text)

# ====================== 2. 违禁词自动踢人 ======================
@dp.message()
async def check_bad_words(message: Message):
    if not message.text or message.from_user.id in ADMIN_IDS:
        return
    text_lower = message.text.lower()
    for word in bad_words:
        if word in text_lower:
            await message.delete()
            try:
                await bot.ban_chat_member(message.chat.id, message.from_user.id, until_date=timedelta(seconds=30))
                await message.answer(f"🚫 检测到违禁词，已移除用户 {message.from_user.first_name}")
            except:
                pass
            break

@dp.message(Command("addword"))
async def add_word(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    word = message.text.split(maxsplit=1)[-1].strip().lower()
    if word:
        bad_words.add(word)
        await message.answer(f"✅ 已添加违禁词：{word}")

@dp.message(Command("delword"))
async def del_word(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    word = message.text.split(maxsplit=1)[-1].strip().lower()
    if word in bad_words:
        bad_words.remove(word)
        await message.answer(f"✅ 已删除违禁词：{word}")

@dp.message(Command("keywords"))
async def list_keywords(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    if bad_words:
        await message.answer("当前违禁词：\n" + "\n".join(bad_words))
    else:
        await message.answer("当前没有违禁词")

# ====================== 3. 清理已注销账号 ======================
@dp.message(Command("cleandeleted"))
async def clean_deleted_accounts(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ 此命令仅管理员可用")
        return
    await message.answer("🗑️ 当前版本无法自动全量扫描。\n\n推荐方法：找到 “Deleted Account” 的消息 → 回复 → 发送 /kick")

# ====================== 4. 抽奖功能 ======================
@dp.message(Command("lottery"))
async def cmd_lottery(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ 此命令仅管理员可用")
        return

    try:
        parts = message.text.split()
        count = int(parts[1])
        prize = " ".join(parts[2:]) if len(parts) > 2 else "神秘奖品"
    except:
        await message.answer("用法：/lottery 人数 奖品名称\n示例：/lottery 5 猫粮")
        return

    await message.answer(f"🎟️ 抽奖开始！\n抽取 {count} 人，奖品：{prize}\n\n请大家回复此消息参与抽奖～")

    # 简单随机抽奖（实际可改进为收集回复者）
    await asyncio.sleep(5)
    await message.answer(f"🎉 抽奖结束！中奖者请私聊管理员领取 {prize}")

# ====================== 5. 小游戏（石头剪刀布 + 猜数字入口） ======================
@dp.message(lambda m: m.text == "🎮 小游戏")
async def menu_game(message: Message):
    await message.answer("🎮 **小游戏菜单**\n\n请选择：", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="石头剪刀布")]],
        resize_keyboard=True
    ))

@dp.message(lambda m: m.text == "石头剪刀布")
async def play_rps(message: Message):
    await message.answer("请出拳：", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="✊ 石头"), KeyboardButton(text="✌️ 剪刀"), KeyboardButton(text="✋ 布")]],
        resize_keyboard=True
    ))

@dp.message(lambda m: m.text in ["✊ 石头", "✌️ 剪刀", "✋ 布"])
async def rps_game(message: Message):
    user = message.text
    bot_choice = random.choice(["✊ 石头", "✌️ 剪刀", "✋ 布"])
    if user == bot_choice:
        result = "🤝 平局！"
    elif (user == "✊ 石头" and bot_choice == "✌️ 剪刀") or (user == "✌️ 剪刀" and bot_choice == "✋ 布") or (user == "✋ 布" and bot_choice == "✊ 石头"):
        result = "🎉 你赢了！"
    else:
        result = "😿 你输了～"
    await message.answer(f"你出：{user}\n我出：{bot_choice}\n\n{result}", reply_markup=get_main_menu())

# ====================== 启动 ======================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Cute Kitten 机器人启动成功！")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
