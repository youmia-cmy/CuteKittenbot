from aiogram import Router, F
from aiogram.types import Message
from config import DEFAULT_BAD_WORDS
import sqlite3

moder_router = Router()
bad_words = set(DEFAULT_BAD_WORDS)  # 内存缓存，实际建议用数据库

# 加载/保存违禁词（简单用 set，生产建议用数据库）
@moder_router.message(Command("addword"), IsAdmin())
async def add_word(message: Message):
    word = message.text.split(maxsplit=1)[-1].strip().lower()
    if word:
        bad_words.add(word)
        await message.answer(f"✅ 已添加违禁词：{word}")

@moder_router.message(Command("delword"), IsAdmin())
async def del_word(message: Message):
    word = message.text.split(maxsplit=1)[-1].strip().lower()
    if word in bad_words:
        bad_words.remove(word)
        await message.answer(f"✅ 已删除违禁词：{word}")

@moder_router.message(Command("keywords"), IsAdmin())
async def list_keywords(message: Message):
    await message.answer("当前违禁词：\n" + "\n".join(bad_words) if bad_words else "暂无违禁词")

# 自动检测违禁词并踢人
@moder_router.message(F.text)
async def check_bad_words(message: Message, bot: Bot):
    if not message.text:
        return
    text_lower = message.text.lower()
    for word in bad_words:
        if word in text_lower:
            await message.delete()
            await bot.ban_chat_member(message.chat.id, message.from_user.id, until_date=timedelta(seconds=30))
            await message.answer(f"🚫 检测到违禁词，已移除用户 {message.from_user.first_name}")
            break
