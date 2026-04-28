import asyncio
import logging
import os
import random
from typing import List, Set, Dict

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_USERNAMES = ["Cute_Kitten9", "cutekitten9", "_StarryMiu"]
YOUR_X_USERNAME = "_StarryMiu"
YOUR_WEBSITE = "https://cutekitten.hair/"

# 全局存储
forbidden_words: Set[str] = set()
muted_chats: Set[int] = set()
lottery_state: Dict[int, dict] = {}
number_game_state: Dict[int, int] = {}

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ====================== 抽奖状态机 ======================
class LotteryForm(StatesGroup):
    waiting_name = State()
    waiting_link = State()
    waiting_description = State()
    waiting_prize_type = State()
    waiting_prize_amount = State()
    waiting_winner_count = State()
    waiting_draw_time = State()


# ====================== 管理员检查 ======================
async def is_admin(message: Message) -> bool:
    if not message.from_user:
        return False
    username = (message.from_user.username or "").lower()
    if username in [u.lower() for u in ADMIN_USERNAMES]:
        return True
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except:
        return False


# ====================== 键盘 ======================
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 查询代币"), KeyboardButton(text="🎮 小游戏")],
            [KeyboardButton(text="🎟️ 抽奖"), KeyboardButton(text="  我的X主页")],
            [KeyboardButton(text="⚙️ 设置"), KeyboardButton(text="📋 帮助")],
            [KeyboardButton(text="🔇 全体禁言"), KeyboardButton(text="🔊 解除禁言")],
            [KeyboardButton(text="🚪 踢人"), KeyboardButton(text="🚫 封禁")],
        ],
        resize_keyboard=True
    )


def get_game_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✊ 猜拳"), KeyboardButton(text="🔢 猜数字")],
            [KeyboardButton(text="返回主菜单")]
        ],
        resize_keyboard=True
    )


def get_rps_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="石头"), KeyboardButton(text="剪刀"), KeyboardButton(text="布")]],
        resize_keyboard=True
    )


async def auto_delete(msg: Message, delay: int = 25):
    if not msg or not msg.text:
        return
    text = msg.text
    if any(k in text for k in ["猜拳", "猜数字", "你出：", "猜对了", "http", "x.com", "cutekitten.hair"]):
        return
    try:
        await asyncio.sleep(delay)
        await msg.delete()
    except:
        pass


# ====================== 抽奖流程 ======================
@dp.message(lambda m: "抽奖" in m.text)
async def menu_lottery(message: Message, state: FSMContext):
    if not await is_admin(message):
        await message.answer("❌ 权限不足")
        return

    await state.set_state(LotteryForm.waiting_name)
    await message.answer(
        "🎟️ **新建抽奖活动**\n\n"
        "第一步：请输入 **活动名称**（支持中文/英文，例如：100 USDT 空投 或 NFT 抽奖）",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ 取消", callback_data="cancel_lottery")]
        ])
    )


@dp.message(StateFilter(LotteryForm.waiting_name))
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(LotteryForm.waiting_link)
    await message.answer("第二步：请输入 **活动链接**（可发送 /skip 跳过）")


@dp.message(StateFilter(LotteryForm.waiting_link))
async def process_link(message: Message, state: FSMContext):
    link = "无" if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(link=link)
    await state.set_state(LotteryForm.waiting_description)
    await message.answer("第三步：请输入 **活动描述**（可发送 /skip 跳过）")


@dp.message(StateFilter(LotteryForm.waiting_description))
async def process_description(message: Message, state: FSMContext):
    desc = "无" if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(description=desc)
    await state.set_state(LotteryForm.waiting_prize_type)
    await message.answer("第四步：请输入 **奖品类型**（例如：USDT、NFT、实体礼品）")


@dp.message(StateFilter(LotteryForm.waiting_prize_type))
async def process_prize_type(message: Message, state: FSMContext):
    await state.update_data(prize_type=message.text.strip())
    await state.set_state(LotteryForm.waiting_prize_amount)
    await message.answer("第五步：请输入 **奖品数量**（例如：100）")


@dp.message(StateFilter(LotteryForm.waiting_prize_amount))
async def process_prize_amount(message: Message, state: FSMContext):
    await state.update_data(prize_amount=message.text.strip())
    await state.set_state(LotteryForm.waiting_winner_count)
    await message.answer("第六步：请输入 **中奖人数**（例如：5）")


@dp.message(StateFilter(LotteryForm.waiting_winner_count))
async def process_winner_count(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        await state.update_data(winner_count=count)
        await state.set_state(LotteryForm.waiting_draw_time)
        await message.answer("第七步：请输入 **开奖时间**（例如：2026-04-30 20:00）")
    except ValueError:
        await message.answer("❌ 请输入正确的数字")


@dp.message(StateFilter(LotteryForm.waiting_draw_time))
async def process_draw_time(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = message.chat.id

    lottery_state[chat_id] = {
        "name": data["name"],
        "link": data.get("link", "无"),
        "description": data.get("description", "无"),
        "prize_type": data["prize_type"],
        "prize_amount": data["prize_amount"],
        "winner_count": data["winner_count"],
        "draw_time": message.text.strip(),
        "participants": []
    }

    preview = (
        f"🎟️ <b>抽奖活动预览</b>\n\n"
        f"📌 活动名称：{data['name']}\n"
        f"🔗 链接：{data.get('link', '无')}\n"
        f"📝 描述：{data.get('description', '无')}\n"
        f"🎁 奖品：{data['prize_type']} × {data['prize_amount']}\n"
        f"👑 中奖人数：{data['winner_count']} 人\n"
        f"🕒 开奖时间：{message.text}\n\n"
        f"回复任意消息即可参与！"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ 发布抽奖", callback_data="publish_lottery")],
        [InlineKeyboardButton(text="❌ 取消", callback_data="cancel_lottery")]
    ])

    await message.answer(preview, reply_markup=keyboard)
    await state.clear()


@dp.callback_query(lambda c: c.data == "publish_lottery")
async def publish_lottery(callback: CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id not in lottery_state:
        await callback.answer("抽奖已过期")
        return

    state = lottery_state[chat_id]
    text = (
        f"🎉 <b>抽奖活动正式发布！</b>\n\n"
        f"📌 {state['name']}\n"
        f"🔗 {state.get('link', '无')}\n"
        f"📝 {state.get('description', '无')}\n"
        f"🎁 奖品：{state['prize_type']} × {state['prize_amount']}\n"
        f"👑 中奖人数：{state['winner_count']} 人\n"
        f"🕒 开奖时间：{state['draw_time']}\n\n"
        f"❤️ 回复任意消息参与抽奖！\n"
        f"管理员发送 /draw 开奖"
    )

    await callback.message.edit_text(text)
    await callback.answer("✅ 已发布到群里！")


@dp.callback_query(lambda c: c.data == "cancel_lottery")
async def cancel_lottery(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    chat_id = callback.message.chat.id
    lottery_state.pop(chat_id, None)
    await callback.message.edit_text("❌ 抽奖已取消")
    await callback.answer()


# ====================== 抽奖参与 ======================
@dp.message(lambda m: m.chat.id in lottery_state)
async def lottery_join(message: Message):
    state = lottery_state[message.chat.id]
    if message.from_user.id not in state["participants"]:
        state["participants"].append(message.from_user.id)
        await message.answer(f"✅ 参与成功！当前人数：{len(state['participants'])}", delete_after=10)


# ====================== 开奖 ======================
@dp.message(Command("draw"))
async def cmd_draw(message: Message):
    if not await is_admin(message) or message.chat.id not in lottery_state:
        return
    state = lottery_state[message.chat.id]
    if not state["participants"]:
        await message.answer("❌ 暂无参与者")
        return
    count = min(state["winner_count"], len(state["participants"]))
    winners = random.sample(state["participants"], count)
    mentions = [f"<a href='tg://user?id={w}'>用户{w}</a>" for w in winners]
    await message.answer(
        f"🎉 <b>抽奖结果</b>\n\n"
        f"活动：{state['name']}\n"
        f"奖品：{state['prize_type']} × {state['prize_amount']}\n"
        f"中奖者：{', '.join(mentions)}"
    )
    del lottery_state[message.chat.id]


# ====================== 基础命令 ======================
@dp.message(Command("start", "menu"))
async def cmd_start(message: Message):
    await message.answer("😺 喵～ <b>Cute Kitten</b> 机器人启动成功！", reply_markup=get_main_menu())


@dp.message(lambda m: "查询代币" in m.text)
async def menu_token(message: Message):
    await message.answer("🔍 请发送：<code>/token 0x合约地址</code>")


@dp.message(lambda m: "小游戏" in m.text)
async def menu_game(message: Message):
    await message.answer("🎮 请选择小游戏：", reply_markup=get_game_menu())


@dp.message(lambda m: "我的X主页" in m.text or "X主页" in m.text)
async def menu_x_profile(message: Message):
    await message.answer(f"""  <b>我的 X 主页</b>
https://x.com/{YOUR_X_USERNAME}

  <b>官网</b>
{YOUR_WEBSITE}""")


@dp.message(lambda m: "设置" in m.text)
async def menu_settings(message: Message):
    if await is_admin(message):
        await message.answer("⚙️ 管理员设置已开启", reply_markup=get_main_menu())
    else:
        await message.answer("❌ 权限不足")


@dp.message(lambda m: "帮助" in m.text)
async def menu_help(message: Message):
    await message.answer("使用下方菜单即可")


@dp.message(lambda m: "全体禁言" in m.text)
async def menu_mute(message: Message):
    if not await is_admin(message):
        return
    muted_chats.add(message.chat.id)
    try:
        await bot.restrict_chat_member(message.chat.id, 0, permissions=ChatPermissions(can_send_messages=False))
        await message.answer("🔇 已开启全体禁言")
    except:
        await message.answer("❌ 操作失败")


@dp.message(lambda m: "解除禁言" in m.text)
async def menu_unmute(message: Message):
    if not await is_admin(message):
        return
    muted_chats.discard(message.chat.id)
    try:
        await bot.restrict_chat_member(message.chat.id, 0, permissions=ChatPermissions(can_send_messages=True))
        await message.answer("🔊 已解除全体禁言")
    except:
        await message.answer("❌ 操作失败")


@dp.message(lambda m: "踢人" in m.text)
async def menu_kick(message: Message):
    await message.answer("👢 请回复要踢出的用户消息，然后发送 /kick")


@dp.message(lambda m: "封禁" in m.text)
async def menu_ban(message: Message):
    await message.answer("🚫 请回复要封禁的用户消息，然后发送 /ban")


@dp.message(lambda m: "返回主菜单" in m.text)
async def back_to_menu(message: Message):
    await message.answer("✅ 已返回主菜单", reply_markup=get_main_menu())


# ====================== 小游戏 ======================
@dp.message(lambda m: m.text in ["猜拳", "✊ 猜拳"])
async def game_rps(message: Message):
    await message.answer("✊ 猜拳开始！请选择：", reply_markup=get_rps_keyboard())


@dp.message(lambda m: m.text in ["石头", "剪刀", "布"])
async def play_rps(message: Message):
    user_choice = message.text
    bot_choice = random.choice(["石头", "剪刀", "布"])
    if user_choice == bot_choice:
        result = "🤝 平局！"
    elif (user_choice == "石头" and bot_choice == "剪刀") or (user_choice == "剪刀" and bot_choice == "布") or (user_choice == "布" and bot_choice == "石头"):
        result = "🎉 你赢了！"
    else:
        result = "😿 你输了～"
    await message.answer(f"你出：{user_choice}\n我出：{bot_choice}\n\n{result}", reply_markup=get_rps_keyboard())


@dp.message(lambda m: "猜数字" in m.text)
async def start_guess_number(message: Message):
    target = random.randint(1, 100)
    number_game_state[message.chat.id] = target
    await message.answer("🔢 我想了一个 1-100 的数字，回复数字猜猜看！", reply_markup=get_game_menu())


@dp.message(lambda m: m.chat.id in number_game_state and m.text.isdigit())
async def guess_number(message: Message):
    guess = int(message.text)
    target = number_game_state[message.chat.id]
    if guess == target:
        await message.answer("🎉 恭喜猜对了！", reply_markup=get_game_menu())
        del number_game_state[message.chat.id]
    elif guess < target:
        await message.answer("📈 太小了～")
    else:
        await message.answer("📉 太大了～")


# ====================== 代币查询 ======================
@dp.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ 用法：<code>/token 0x合约地址</code>")
        return
    address = parts[1].strip().lower()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}") as resp:
                data = await resp.json()
                if not data.get("pairs"):
                    await message.answer("❌ 未找到交易对")
                    return
                pair = data["pairs"][0]
                base = pair.get("baseToken", {})
                text = f"🪙 <b>{base.get('name')}</b> ({base.get('symbol')})\n💰 ${pair.get('priceUsd', 'N/A')}"
                await message.answer(text)
    except:
        await message.answer("❌ 查询失败")


# ====================== 违禁词过滤 ======================
@dp.message()
async def word_filter(message: Message):
    if not message.text:
        return
    text_lower = message.text.lower()
    for word in list(forbidden_words):
        if word in text_lower:
            try:
                await message.delete()
                await message.answer("🚫 违禁词，已删除", delete_after=5)
            except:
                pass
            return


# ====================== 启动 ======================
async def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("🚀 Cute Kitten 机器人启动成功！")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
