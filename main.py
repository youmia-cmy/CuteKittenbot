import asyncio
import logging
import os
import random
from typing import List, Set

import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ChatPermissions

# ====================== 配置 ======================
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 管理员队列
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
ADMIN_USERNAMES = ["Cute_Kitten9", "_StarryMiu"]

YOUR_X_USERNAME = "_StarryMiu"
YOUR_WEBSITE = "https://cutekitten.hair/"

# 全局存储
forbidden_words: Set[str] = set()
muted_chats: Set[int] = set()
lottery_participants: List[int] = []
number_game_state = {}

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ====================== 管理员检查 ======================
async def is_admin(message: Message) -> bool:
    user = message.from_user
    if user.id in ADMIN_IDS or (user.username and user.username.lower() in [u.lower() for u in ADMIN_USERNAMES]):
        return True
    try:
        member = await bot.get_chat_member(message.chat.id, user.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except:
        return False


# ====================== 键盘 ======================
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 查询代币"), KeyboardButton(text="🎮 小游戏")],
            [KeyboardButton(text="🎟️ 抽奖"), KeyboardButton(text=" 我的X主页")],
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


# ====================== 基础命令 ======================
@dp.message(Command("start", "menu"))
async def cmd_start(message: Message):
    await message.answer(
        "😺 喵～ <b>Cute Kitten</b> 机器人启动成功！\n请选择下方功能：",
        reply_markup=get_main_menu()
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = (
        "📋 <b>所有可用命令</b>\n\n"
        "/start 或 /menu —— 打开主菜单\n"
        "/help —— 显示此帮助\n"
        "/token 0x地址 —— 查询代币信息\n"
        "/lottery 人数 奖品 —— 启动抽奖\n"
        "/draw —— 抽取获奖者\n"
        "/mute —— 全体禁言（管理员）\n"
        "/unmute —— 解除全体禁言（管理员）\n"
        "/kick —— 踢出用户（回复消息）\n"
        "/ban —— 封禁用户（回复消息）\n"
        "/addword 词 —— 添加违禁词（管理员）\n"
        "/delword 词 —— 删除违禁词（管理员）\n"
        "/settings —— 查看机器人设置（管理员）\n"
        "/myid —— 查看你的用户ID"
    )
    await message.answer(help_text, reply_markup=get_main_menu())


@dp.message(Command("myid"))
async def cmd_myid(message: Message):
    await message.answer(f"🆔 你的用户 ID 是：\n<code>{message.from_user.id}</code>")


# ====================== 主菜单按钮处理 ======================
@dp.message(lambda m: "查询代币" in m.text)
async def menu_token(message: Message):
    await message.answer("🔍 请发送：<code>/token 0x合约地址</code>")


@dp.message(lambda m: "小游戏" in m.text)
async def menu_game(message: Message):
    await message.answer("🎮 请选择小游戏：", reply_markup=get_game_menu())


@dp.message(lambda m: "抽奖" in m.text)
async def menu_lottery(message: Message):
    await message.answer("🎟️ 发送：<code>/lottery 人数 奖品名称</code> 来启动抽奖")


@dp.message(lambda m: "我的X主页" in m.text or "X主页" in m.text)
async def menu_x_profile(message: Message):
    text = f"""🐦 <b>我的 X 主页</b>
https://x.com/{YOUR_X_USERNAME}

🌐 <b>我的官网</b>
{YOUR_WEBSITE}"""
    await message.answer(text)


@dp.message(lambda m: "设置" in m.text)
async def menu_settings(message: Message):
    if await is_admin(message):
        await message.answer("⚙️ 管理员设置菜单", reply_markup=get_main_menu())
    else:
        await message.answer("⚙️ 普通用户暂无权限～")


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
    await message.answer("👢 请回复要踢出的用户消息，然后输入 /kick")


@dp.message(lambda m: "封禁" in m.text)
async def menu_ban(message: Message):
    await message.answer("🚫 请回复要封禁的用户消息，然后输入 /ban")


@dp.message(lambda m: "返回主菜单" in m.text)
async def back_to_menu(message: Message):
    await message.answer("✅ 已返回主菜单", reply_markup=get_main_menu())


# ====================== 小游戏 ======================
@dp.message(lambda m: m.text in ["猜拳", "✊ 猜拳"])
async def game_rps(message: Message):
    await message.answer("✊ 猜拳开始！请选择你的手势：", reply_markup=get_rps_keyboard())


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
    await message.answer(f"你出：{user_choice}\n我出：{bot_choice}\n\n{result}", reply_markup=get_rps_keyboard())


@dp.message(lambda m: "猜数字" in m.text or "🔢 猜数字" in m.text)
async def start_guess_number(message: Message):
    target = random.randint(1, 100)
    number_game_state[message.chat.id] = target
    await message.answer(
        "🔢 我在 1-100 之间想了一个数字\n回复数字进行猜测！",
        reply_markup=get_game_menu()
    )


@dp.message(lambda m: m.chat.id in number_game_state and m.text.isdigit())
async def guess_number(message: Message):
    guess = int(message.text)
    target = number_game_state[message.chat.id]
    if guess == target:
        await message.answer("🎉 恭喜你猜对了！", reply_markup=get_game_menu())
        del number_game_state[message.chat.id]
    elif guess < target:
        await message.answer("📈 太小了，再试试～")
    else:
        await message.answer("📉 太大了，再试试～")


# ====================== 代币查询 ======================
@dp.message(Command("token"))
async def cmd_token(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ 用法：<code>/token 0x合约地址</code>")
        return
    address = parts[1].strip().lower()
    if not address.startswith("0x"):
        await message.answer("❌ 请提供有效的 0x 开头合约地址")
        return

    await message.answer("🔍 正在从 DexScreener 查询...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}") as resp:
                data = await resp.json()
                if not data.get("pairs"):
                    await message.answer("❌ 未找到该代币的交易对")
                    return
                pair = data["pairs"][0]
                base = pair.get("baseToken", {})
                text = (
                    f"🪙 <b>{base.get('name', 'Unknown')}</b> ({base.get('symbol', 'N/A')})\n"
                    f"🔗 地址：<code>{address}</code>\n"
                    f"💰 当前价格：${pair.get('priceUsd', 'N/A')}\n"
                    f"💧 流动性：${pair.get('liquidity', {}).get('usd', 'N/A')}\n"
                    f"📊 24h 成交量：${pair.get('volume', {}).get('h24', 'N/A')}"
                )
                await message.answer(text)
    except Exception as e:
        logging.error(f"Token query error: {e}")
        await message.answer("❌ 查询失败，请稍后再试")


# ====================== 抽奖系统 ======================
@dp.message(Command("lottery"))
async def cmd_lottery(message: Message):
    if not await is_admin(message):
        await message.answer("❌ 仅管理员可启动抽奖")
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("❌ 用法：<code>/lottery 人数 [奖品名称]</code>")
        return
    try:
        count = int(parts[1])
    except:
        await message.answer("❌ 人数必须是数字")
        return
    prize = parts[2] if len(parts) > 2 else "神秘奖品"

    global lottery_participants
    lottery_participants = []
    await message.answer(
        f"🎟️ <b>抽奖已开启！</b>\n"
        f"奖品：{prize}\n"
        f"参与人数上限：{count}\n\n"
        "回复任意消息即可参与抽奖～"
    )


@dp.message(lambda m: isinstance(lottery_participants, list) and len(lottery_participants) < 200)
async def lottery_join(message: Message):
    global lottery_participants
    if message.from_user.id not in lottery_participants:
        lottery_participants.append(message.from_user.id)
        await message.answer(f"✅ 参与成功！当前人数：{len(lottery_participants)}")


@dp.message(Command("draw"))
async def cmd_draw(message: Message):
    if not await is_admin(message):
        return
    global lottery_participants
    if not lottery_participants:
        await message.answer("❌ 当前没有参与者")
        return
    winners = random.sample(lottery_participants, min(1, len(lottery_participants)))
    mentions = [f"<a href='tg://user?id={wid}'>用户{wid}</a>" for wid in winners]
    await message.answer(f"🎉 <b>抽奖结果</b>\n中奖者：{', '.join(mentions)}")
    lottery_participants = []


# ====================== 管理员功能 ======================
@dp.message(Command("mute"))
async def cmd_mute(message: Message):
    if not await is_admin(message):
        await message.answer("❌ 权限不足")
        return
    muted_chats.add(message.chat.id)
    try:
        await bot.restrict_chat_member(
            message.chat.id, 
            user_id=0, 
            permissions=ChatPermissions(can_send_messages=False)
        )
        await message.answer("🔇 已开启全体禁言（仅管理员可发言）")
    except Exception as e:
        await message.answer(f"❌ 操作失败：{e}")


@dp.message(Command("unmute"))
async def cmd_unmute(message: Message):
    if not await is_admin(message):
        await message.answer("❌ 权限不足")
        return
    if message.chat.id in muted_chats:
        muted_chats.remove(message.chat.id)
    try:
        await bot.restrict_chat_member(
            message.chat.id, 
            user_id=0, 
            permissions=ChatPermissions(can_send_messages=True)
        )
        await message.answer("🔊 已解除全体禁言")
    except Exception as e:
        await message.answer(f"❌ 操作失败：{e}")


@dp.message(Command("kick"))
async def cmd_kick(message: Message):
    if not await is_admin(message):
        await message.answer("❌ 权限不足")
        return
    if not message.reply_to_message:
        await message.answer("❌ 请回复要踢出的用户消息")
        return
    user_id = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_id, revoke_messages=False)
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.answer(f"👢 已踢出用户 <code>{user_id}</code>")
    except Exception as e:
        await message.answer(f"❌ 操作失败：{e}")


@dp.message(Command("ban"))
async def cmd_ban(message: Message):
    if not await is_admin(message):
        await message.answer("❌ 权限不足")
        return
    if not message.reply_to_message:
        await message.answer("❌ 请回复要封禁的用户消息")
        return
    user_id = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        await message.answer(f"🚫 已永久封禁用户 <code>{user_id}</code>")
    except Exception as e:
        await message.answer(f"❌ 操作失败：{e}")


@dp.message(Command("addword"))
async def cmd_addword(message: Message):
    if not await is_admin(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ 用法：<code>/addword 违禁词</code>")
        return
    word = parts[1].strip().lower()
    forbidden_words.add(word)
    await message.answer(f"✅ 已添加违禁词：{word}")


@dp.message(Command("delword"))
async def cmd_delword(message: Message):
    if not await is_admin(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ 用法：<code>/delword 违禁词</code>")
        return
    word = parts[1].strip().lower()
    if word in forbidden_words:
        forbidden_words.remove(word)
        await message.answer(f"✅ 已删除违禁词：{word}")
    else:
        await message.answer("❌ 该词不在违禁列表中")


@dp.message(Command("settings"))
async def cmd_settings(message: Message):
    if not await is_admin(message):
        await message.answer("❌ 权限不足")
        return
    await message.answer(
        f"⚙️ <b>机器人设置</b>\n\n"
        f"违禁词数量：{len(forbidden_words)}\n"
        f"全体禁言状态：{'已开启' if message.chat.id in muted_chats else '未开启'}",
        reply_markup=get_main_menu()
    )


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
                await message.answer("🚫 消息包含违禁词，已自动删除", delete_after=5)
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
