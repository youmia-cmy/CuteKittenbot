from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from utils.filters import IsAdmin
from aiogram import Bot
from datetime import timedelta

admin_router = Router()

@admin_router.message(Command("mute"), IsAdmin())
async def cmd_mute(message: Message, bot: Bot):
    await bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=message.chat.id,  # 全体禁言用 chat id 作为 user_id 的特殊方式，实际推荐设置 default permissions
        permissions=types.ChatPermissions(can_send_messages=False)
    )
    await message.answer("✅ 已全体禁言（仅管理员可发言）")

@admin_router.message(Command("unmute"), IsAdmin())
async def cmd_unmute(message: Message, bot: Bot):
    await bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=message.chat.id,
        permissions=types.ChatPermissions(can_send_messages=True, can_send_photos=True, can_send_videos=True)
    )
    await message.answer("✅ 已解除全体禁言")

@admin_router.message(Command("ban"), IsAdmin())
async def cmd_ban(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer("请回复要封禁的用户消息")
        return
    user_id = message.reply_to_message.from_user.id
    await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id)
    await message.answer(f"✅ 已封禁用户 {user_id}")

@admin_router.message(Command("kick"), IsAdmin())
async def cmd_kick(message: Message, bot: Bot):
    if not message.reply_to_message:
        await message.answer("请回复要移除的用户消息")
        return
    user_id = message.reply_to_message.from_user.id
    await bot.ban_chat_member(chat_id=message.chat.id, user_id=user_id, until_date=timedelta(seconds=30))  # 30秒后自动解封 = kick
    await message.answer(f"✅ 已移除用户 {user_id}")
