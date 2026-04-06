from aiogram import Router, Bot
from aiogram.types import ChatMemberUpdated
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from config import WELCOME_TEXT

welcome_router = Router()

@welcome_router.chat_member(
    ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER)
)
async def welcome_new_member(event: ChatMemberUpdated, bot: Bot):
    user = event.new_chat_member.user
    chat_id = event.chat.id
    
    text = WELCOME_TEXT.format(name=user.first_name or user.username or "新朋友")
    
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
