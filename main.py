import asyncio
import logging
import os
import random
from typing import List, Set, Dict

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ChatPermissions

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS: List[int] = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
ADMIN_USERNAMES = ["Cute_Kitten9", "_StarryMiu", "cutekitten9"]

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
dp = Dispatcher()

# ====================== 管理员检查 ======================
async def is_admin(message: Message) -> bool:
    if not message.from_user:
        return False
    user = message.from_user
    user_id = user.id
    username = (user.username or "").lower()

    if user_id in ADMIN_IDS or username in [u.lower() for u in ADMIN_USERNAMES]:
        logging.info(f"✅ 硬编码管理员: {user_id} @{username}")
        return True

    try:
        member = await bot.get_chat_member(message.chat.id, user_id)
        if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]:
            logging.info(f"✅ 群管理员: {user_id} @{username}")
            return True
    except Exception as e:
        logging.warning(f"获取成员信息失败: {e}")

    logging.warning(f"❌ 非管理员: {user_id} @{username}")
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
        keyboard=[
            [KeyboardButton(text="石头"), KeyboardButton(text="剪刀"), KeyboardButton(text="布")]
        ],
        resize_keyboard=True
    )


# ====================== 自动删除机器人消息 ======================
async def auto_delete(msg: Message, delay: int = 25):
    if not msg:
        return
    text = msg.text or ""
    if any(k in text for k in ["猜拳", "猜数字", "你出：", "猜对了", "http", "x.com", "cutekitten.hair"]):
        return
    try:
        await asyncio.sleep(delay)
        await msg.delete()
    except:
        pass


# ====================== 测试权限 ======================
@dp.message(Command("testadmin"))
async def test_admin(message: Message):
    is_ad = await is_admin(message)
    await message.answer(
        f"🧪 <b>权限测试</b>\n"
        f"用户ID: <code>{message.from_user.id}</code>\n"
        f"用户名: @{message.from_user.username}\n"
        f"是否管理员: {'✅ 是' if is_ad else '❌ 否'}"
    )


# ====================== 基础命令 ======================
@dp.message(Command("start", "menu"))
async def cmd_start(message: Message):
    sent = await message.answer(
        "😺 喵～ <b>Cute Kitten</b> 机器人启动成功！\n请选择下方功能：",
        reply_markup=get_main_menu()
    )
    await auto_delete(sent)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    sent = await message.answer(
        "📋 <b>所有可用命令</b>\n\n"
        "/start /menu — 打开主菜单\n"
        "/testadmin — 测试自己权限\n"
        "/token 0x地址 — 查询代币\n"
        "/lottery — 抽奖\n"
        "/draw — 开奖\n"
        "/mute — 全体禁言\n"
        "/unmute — 解除禁言\n"
        "/kick — 踢人（回复消息）\n"
        "/ban — 封禁（回复消息）\n"
        "/addword 词 — 添加违禁词\n"
        "/delword 词 — 删除违禁词\n"
        "/settings — 设置",
        reply_markup=get_main_menu()
    )
    await auto_delete(sent)


@dp.message(Command("myid"))
async def cmd_myid(message: Message):
    sent = await message.answer(f"🆔 你的用户 ID 是：\n<code>{message.from_user.id}</code>")
    await auto_delete(sent)


# ====================== 主菜单按钮 ======================
@dp.message(lambda m: "查询代币" in m.text)
async def menu_token(message: Message):
    sent = await message.answer("🔍 请发送：<code>/token 0x合约地址</code>")
    await auto_delete(sent)


@dp.message(lambda m: "小游戏" in m.text)
async def menu_game(message: Message):
    sent = await message.answer("🎮 请选择小游戏：", reply_markup=get_game_menu())
    await auto_delete(sent, 60)


@dp.message(lambda m: "抽奖" in m.text)
async def menu_lottery(message: Message):
    if not await is_admin(message):
        sent = await message.answer("❌ 权限不足\n请发送 /testadmin 测试")
        await auto_delete(sent)
        return
    lottery_state[message.chat.id] = {"participants": [], "prize": "神秘奖品"}
    sent = await message.answer("🎟️ 抽奖已开启！回复任意消息即可参与\n管理员可随时发送 /draw 开奖")
    await auto_delete(sent, 60)


@dp.message(lambda m: "我的X主页" in m.text or "X主页" in m.text)
async def menu_x_profile(message: Message):
    text = f"""  <b>我的 X 主页</b>
https://x.com/{YOUR_X_USERNAME}

  <b>我的官网</b>
{YOUR_WEBSITE}"""
    await message.answer(text)


@dp.message(lambda m: "设置" in m.text)
async def menu_settings(message: Message):
    if await is_admin(message):
        sent = await message.answer("⚙️ 管理员设置已开启", reply_markup=get_main_menu())
        await auto_delete(sent)
    else:
        sent = await message.answer("❌ 权限不足")
        await auto_delete(sent)


@dp.message(lambda m: "帮助" in m.text or "📋 帮助" in m.text)
async def menu_help(message: Message):
    await cmd_help(message)


@dp.message(lambda m: "全体禁言" in m.text)
async def menu_mute(message: Message):
    await cmd_mute(message)


@dp.message(lambda m: "解除禁言" in m.text)
async def menu_unmute(message: Message):
    await cmd_unmute(message)


@dp.message(lambda m: "踢人" in m.text)
async def menu_kick(message: Message):
    sent = await message.answer("👢 请回复要踢出的用户消息，然后发送 /kick")
    await auto_delete(sent)


@dp.message(lambda m: "封禁" in m.text)
async def menu_ban(message: Message):
    sent = await message.answer("🚫 请回复要封禁的用户消息，然后发送 /ban")
    await auto_delete(sent)


@dp.message(lambda m: "返回主菜单" in m.text)
async def back_to_menu(message: Message):
    sent = await message.answer("✅ 已返回主菜单", reply_markup=get_main_menu())
    await auto_delete(sent)


# ====================== 小游戏 ======================
@dp.message(lambda m: m.text in ["猜拳", "✊ 猜拳"])
async def game_rps(message: Message):
    sent = await message.answer("✊ 猜拳开始！请选择：", reply_markup=get_rps_keyboard())
    await auto_delete(sent, 120)


@dp.message(lambda m: m.text in ["石头", "剪刀", "布"])
async def play_rps(message: Message):
    user_choice = message.text
    bot_choice = random.choice(["石头", "剪刀", "布"])
    if user_choice == bot_choice:
        result = "🤝 平局！"
    elif (user_choice == "石头" and bot_choice == "剪刀") or \
         (user_choice == "剪刀" and bot_choice == "布") or \
         (user_choice == "布" and bot_choice == "石头"):
        result = "🎉 你赢了！"
    else:
        result = "😿 你输了～"
    sent = await message.answer(
        f"你出：{user_choice}\n我出：{bot_choice}\n\n{result}",
        reply_markup=get_rps_keyboard()
    )
    await auto_delete(sent, 120)


@dp.message(lambda m: "猜数字" in m.text or "🔢 猜数字" in m.text)
async def start_guess_number(message: Message):
    target = random.randint(1, 100)
    number_game_state[message.chat.id] = target
    sent = await message.answer(
        "🔢 我在 1-100 之间想了一个数字\n回复数字进行猜测！",
        reply_markup=get_game_menu()
    )
    await auto_delete(sent, 180)


@dp.message(lambda m: m.chat.id in number_game_state and m.text.isdigit())
async def guess_number(message: Message):
    guess = int(message.text)
    target = number_game_state[message.chat.id]
    if guess == target:
        sent = await message.answer("🎉 恭喜你猜对了！", reply_markup=get_game_menu())
        del number_game_state[message.chat.id]
    elif guess < target:
        sent = await message.answer("📈 太小了，再试试～")
    else:
        sent = await message.answer("📉 太大了，再试试～")
    await auto_delete(sent, 60)


# ====================== 代币查询 ======================
@dp.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        sent = await message.answer("❌ 用法：<code>/token 0x合约地址</code>")
        await auto_delete(sent)
        return
    address = parts[1].strip().lower()
    if not address.startswith("0x"):
        sent = await message.answer("❌ 请提供有效的 0x 开头合约地址")
        await auto_delete(sent)
        return

    await message.answer("🔍 正在查询...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}") as resp:
                data = await resp.json()
                if not data.get("pairs"):
                    sent = await message.answer("❌ 未找到交易对")
                    await auto_delete(sent)
                    return
                pair = data["pairs"][0]
                base = pair.get("baseToken", {})
                text = (
                    f"🪙 <b>{base.get('name', 'Unknown')}</b> ({base.get('symbol', 'N/A')})\n"
                    f"🔗 <code>{address}</code>\n"
                    f"💰 价格: ${pair.get('priceUsd', 'N/A')}\n"
                    f"💧 流动性: ${pair.get('liquidity', {}).get('usd', 'N/A')}"
                )
                sent = await message.answer(text)
                await auto_delete(sent)
    except Exception as e:
        logging.error(f"Token error: {e}")
        sent = await message.answer("❌ 查询失败，请稍后再试")
        await auto_delete(sent)


# ====================== 抽奖 ======================
@dp.message(Command("lottery"))
async def cmd_lottery(message: Message):
    await menu_lottery(message)


@dp.message(lambda m: m.chat.id in lottery_state)
async def lottery_join(message: Message):
    state = lottery_state[message.chat.id]
    if message.from_user.id not in state["participants"]:
        state["participants"].append(message.from_user.id)
        await message.answer(f"✅ 参与成功！当前人数：{len(state['participants'])}", delete_after=10)


@dp.message(Command("draw"))
async def cmd_draw(message: Message):
    if not await is_admin(message) or message.chat.id not in lottery_state:
        return
    state = lottery_state[message.chat.id]
    if not state["participants"]:
        await message.answer("❌ 暂无参与者")
        return
    winners = random.sample(state["participants"], min(1, len(state["participants"])))
    mentions = [f"<a href='tg://user?id={w}'>用户{w}</a>" for w in winners]
    await message.answer(f"🎉 <b>抽奖结果</b>\n中奖者：{', '.join(mentions)}")
    del lottery_state[message.chat.id]


# ====================== 管理员功能 ======================
@dp.message(Command("mute"))
async def cmd_mute(message: Message):
    if not await is_admin(message):
        sent = await message.answer("❌ 权限不足\n请发送 /testadmin 测试")
        await auto_delete(sent)
        return
    muted_chats.add(message.chat.id)
    try:
        await bot.restrict_chat_member(message.chat.id, 0, permissions=ChatPermissions(can_send_messages=False))
        sent = await message.answer("🔇 已开启全体禁言（仅管理员可发言）")
        await auto_delete(sent)
    except Exception as e:
        sent = await message.answer(f"❌ 操作失败: {e}")
        await auto_delete(sent)


@dp.message(Command("unmute"))
async def cmd_unmute(message: Message):
    if not await is_admin(message):
        sent = await message.answer("❌ 权限不足\n请发送 /testadmin 测试")
        await auto_delete(sent)
        return
    muted_chats.discard(message.chat.id)
    try:
        await bot.restrict_chat_member(message.chat.id, 0, permissions=ChatPermissions(can_send_messages=True))
        sent = await message.answer("🔊 已解除全体禁言")
        await auto_delete(sent)
    except Exception as e:
        sent = await message.answer(f"❌ 操作失败: {e}")
        await auto_delete(sent)


@dp.message(Command("kick"))
async def cmd_kick(message: Message):
    if not await is_admin(message):
        sent = await message.answer("❌ 权限不足")
        await auto_delete(sent)
        return
    if not message.reply_to_message:
        sent = await message.answer("❌ 请回复要踢出的用户消息")
        await auto_delete(sent)
        return
    user_id = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_id, revoke_messages=False)
        await bot.unban_chat_member(message.chat.id, user_id)
        sent = await message.answer(f"👢 已踢出用户 <code>{user_id}</code>")
        await auto_delete(sent)
    except Exception as e:
        sent = await message.answer(f"❌ 操作失败: {e}")
        await auto_delete(sent)


@dp.message(Command("ban"))
async def cmd_ban(message: Message):
    if not await is_admin(message):
        sent = await message.answer("❌ 权限不足")
        await auto_delete(sent)
        return
    if not message.reply_to_message:
        sent = await message.answer("❌ 请回复要封禁的用户消息")
        await auto_delete(sent)
        return
    user_id = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        sent = await message.answer(f"🚫 已封禁用户 <code>{user_id}</code>")
        await auto_delete(sent)
    except Exception as e:
        sent = await message.answer(f"❌ 操作失败: {e}")
        await auto_delete(sent)


@dp.message(Command("addword"))
async def cmd_addword(message: Message):
    if not await is_admin(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        sent = await message.answer("❌ 用法：<code>/addword 违禁词</code>")
        await auto_delete(sent)
        return
    word = parts[1].strip().lower()
    forbidden_words.add(word)
    sent = await message.answer(f"✅ 已添加违禁词：{word}")
    await auto_delete(sent)


@dp.message(Command("delword"))
async def cmd_delword(message: Message):
    if not await is_admin(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        sent = await message.answer("❌ 用法：<code>/delword 违禁词</code>")
        await auto_delete(sent)
        return
    word = parts[1].strip().lower()
    if word in forbidden_words:
        forbidden_words.remove(word)
        sent = await message.answer(f"✅ 已删除违禁词：{word}")
    else:
        sent = await message.answer("❌ 该词不在列表中")
    await auto_delete(sent)


@dp.message(Command("settings"))
async def cmd_settings(message: Message):
    if not await is_admin(message):
        sent = await message.answer("❌ 权限不足")
        await auto_delete(sent)
        return
    sent = await message.answer(
        f"⚙️ <b>机器人设置</b>\n违禁词数量：{len(forbidden_words)}\n"
        f"全体禁言状态：{'已开启' if message.chat.id in muted_chats else '未开启'}"
    )
    await auto_delete(sent)


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
                await message.answer("🚫 包含违禁词，已删除", delete_after=5)
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
