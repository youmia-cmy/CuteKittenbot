import asyncio
import logging
import os
import random
import hashlib
from datetime import datetime
from typing import Set, Dict

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


# ====================== 完整64卦数据库 ======================
HEXAGRAMS = {
    1: {"name": "乾为天", "fortune": "大吉", "judgment": "元亨利贞。", "detail": "乾卦象征天道刚健，自强不息。利于积极行动、开创事业，但需注意勿过刚则折。"},
    2: {"name": "坤为地", "fortune": "吉", "judgment": "元亨，利牝马之贞。", "detail": "坤卦主柔顺、厚德载物。宜守成、包容、顺势而为，不宜主动争先。"},
    3: {"name": "水雷屯", "fortune": "中吉", "judgment": "元亨利贞。勿用有攸往，利建侯。", "detail": "屯卦象征初生艰难。起步阶段需耐心积累，不可急进。"},
    4: {"name": "山水蒙", "fortune": "平", "judgment": "亨。匪我求童蒙，童蒙求我。", "detail": "蒙卦代表启蒙、学习。需虚心求教。"},
    5: {"name": "水天需", "fortune": "吉", "judgment": "有孚，光亨，贞吉。需于酒食。", "detail": "需卦象征等待时机。耐心等待则利。"},
    6: {"name": "天水讼", "fortune": "凶", "judgment": "有孚窒惕，中吉，终凶。", "detail": "讼卦主争讼。宜调解，避免冲突。"},
    7: {"name": "地水师", "fortune": "平", "judgment": "贞丈人吉，无咎。", "detail": "师卦象征用兵、组织。需严明纪律。"},
    8: {"name": "水地比", "fortune": "大吉", "judgment": "吉。原筮元永贞，无咎。", "detail": "比卦主团结。上下和睦大吉。"},
    9: {"name": "风天小畜", "fortune": "平", "judgment": "亨。小畜，密云不雨，自我西郊。", "detail": "小畜卦象征小有积蓄。宜蓄势待发。"},
    10: {"name": "天泽履", "fortune": "吉", "judgment": "履虎尾，不咥人，亨。", "detail": "履卦象征小心行走。谨慎行事，可化险为夷。"},
    11: {"name": "地天泰", "fortune": "大吉", "judgment": "小往大来，吉亨。", "detail": "泰卦主通泰、亨通。天地交泰，万事顺利。"},
    12: {"name": "天地否", "fortune": "凶", "judgment": "否之匪人，不利君子贞，大往小来。", "detail": "否卦主闭塞不通。宜守正待时。"},
    13: {"name": "天火同人", "fortune": "吉", "judgment": "同人于野，亨。利涉大川，利君子贞。", "detail": "同人卦象征与人和同。团结一致则事成。"},
    14: {"name": "火天大有", "fortune": "大吉", "judgment": "大有，元亨。", "detail": "大有卦象征大有收获。富足之时更需谦虚。"},
    15: {"name": "地山谦", "fortune": "吉", "judgment": "谦，亨。君子有终。", "detail": "谦卦主谦逊受益。谦虚则得人助。"},
    16: {"name": "雷地豫", "fortune": "吉", "judgment": "豫，利建侯行师。", "detail": "豫卦象征愉悦。把握时机，行动有利。"},
    17: {"name": "泽雷随", "fortune": "吉", "judgment": "随，元亨利贞，无咎。", "detail": "随卦主随从、顺势。随和则无咎。"},
    18: {"name": "山风蛊", "fortune": "平", "judgment": "蛊，元亨。利涉大川，先甲三日，后甲三日。", "detail": "蛊卦象征整治腐败。需革除旧弊。"},
    19: {"name": "地泽临", "fortune": "吉", "judgment": "临，元亨利贞。至于八月有凶。", "detail": "临卦主临近、监督。宜亲近民众。"},
    20: {"name": "风地观", "fortune": "平", "judgment": "观，盥而不荐，有孚颙若。", "detail": "观卦象征观察。宜以德服人。"},
    21: {"name": "火雷噬嗑", "fortune": "吉", "judgment": "噬嗑，亨。利用狱。", "detail": "噬嗑卦象征去除障碍。需果断处理。"},
    22: {"name": "山火贲", "fortune": "平", "judgment": "贲，亨。小利有攸往。", "detail": "贲卦主文饰。注重形象但不可过度。"},
    23: {"name": "山地剥", "fortune": "凶", "judgment": "剥，不利有攸往。", "detail": "剥卦主衰败。宜静守等待转机。"},
    24: {"name": "地雷复", "fortune": "大吉", "judgment": "复，亨。出入无疾，朋来无咎。反复其道，七日来复，利有攸往。", "detail": "复卦象征复苏。阳气复生，大有希望。"},
    25: {"name": "天雷无妄", "fortune": "吉", "judgment": "无妄，元亨利贞。其匪正有眚，不利有攸往。", "detail": "无妄卦主真实无妄。心诚则灵。"},
    26: {"name": "山天大畜", "fortune": "吉", "judgment": "大畜，利贞。不家食吉，利涉大川。", "detail": "大畜卦象征厚积薄发。"},
    27: {"name": "山雷颐", "fortune": "平", "judgment": "颐，贞吉。观颐，自求口实。", "detail": "颐卦主养身养德。"},
    28: {"name": "泽风大过", "fortune": "凶", "judgment": "大过，栋桡。利有攸往，亨。", "detail": "大过卦象征过度。需勇于变革。"},
    29: {"name": "坎为水", "fortune": "平", "judgment": "习坎，有孚，维心亨。行有尚。", "detail": "坎卦主险阻。需诚信渡险。"},
    30: {"name": "离为火", "fortune": "吉", "judgment": "离，利贞。亨。畜牝牛吉。", "detail": "离卦象征光明。依附正道则吉。"},
    31: {"name": "泽山咸", "fortune": "吉", "judgment": "咸，亨利贞。取女吉。", "detail": "咸卦主感应。真诚相感则事成。"},
    32: {"name": "雷风恒", "fortune": "吉", "judgment": "恒，亨。无咎，利贞。利有攸往。", "detail": "恒卦象征持久。持之以恒则成。"},
    33: {"name": "天山遯", "fortune": "平", "judgment": "遯，亨。小利贞。", "detail": "遯卦主退避。时机不利宜暂退。"},
    34: {"name": "雷天大壮", "fortune": "吉", "judgment": "大壮，利贞。", "detail": "大壮卦象征强盛。守正不妄动。"},
    35: {"name": "火地晋", "fortune": "吉", "judgment": "晋，康侯用锡马蕃庶，昼日三接。", "detail": "晋卦主晋升。积极进取则获赏。"},
    36: {"name": "地火明夷", "fortune": "平", "judgment": "明夷，利艰贞。", "detail": "明夷卦象征韬光养晦。"},
    37: {"name": "风火家人", "fortune": "吉", "judgment": "家人，利女贞。", "detail": "家人卦主家庭和睦。正家风则兴。"},
    38: {"name": "火泽睽", "fortune": "平", "judgment": "睽，小事吉。", "detail": "睽卦主意见不合。小事可成。"},
    39: {"name": "水山蹇", "fortune": "平", "judgment": "蹇，利西南，不利东北。利见大人。", "detail": "蹇卦象征险阻。宜求贤助。"},
    40: {"name": "雷水解", "fortune": "吉", "judgment": "解，利西南。无所往，其来复吉。有攸往，夙吉。", "detail": "解卦主解除困难。及时行动则吉。"},
    41: {"name": "山泽损", "fortune": "平", "judgment": "损，有孚，元吉，无咎，可贞。利有攸往。", "detail": "损卦象征减损。损己利人则吉。"},
    42: {"name": "风雷益", "fortune": "吉", "judgment": "益，利有攸往，利涉大川。", "detail": "益卦主增益。施惠于人则获益。"},
    43: {"name": "泽天夬", "fortune": "平", "judgment": "夬，扬于王庭，孚号有厉。告自邑，不利即戎。利有攸往。", "detail": "夬卦象征决断。清除小人。"},
    44: {"name": "天风姤", "fortune": "平", "judgment": "姤，女壮，勿用取女。", "detail": "姤卦主相遇。防小人。"},
    45: {"name": "泽地萃", "fortune": "吉", "judgment": "萃，亨。王假有庙，利见大人，亨。利贞。用大牲吉。利有攸往。", "detail": "萃卦主聚集。聚众则力强。"},
    46: {"name": "地风升", "fortune": "吉", "judgment": "升，元亨。用见大人，勿恤。南征吉。", "detail": "升卦象征上升。循序渐进则大吉。"},
    47: {"name": "泽水困", "fortune": "凶", "judgment": "困，亨。贞大人吉，无咎。有言不信。", "detail": "困卦主困境。守正则亨通。"},
    48: {"name": "水风井", "fortune": "平", "judgment": "井，改邑不改井。无丧无得。往来井井。汔至亦未繘井，羸其瓶，凶。", "detail": "井卦象征根本。需维护不可废弃。"},
    49: {"name": "泽火革", "fortune": "吉", "judgment": "革，己日乃孚。元亨利贞。悔亡。", "detail": "革卦主变革。时机成熟则吉。"},
    50: {"name": "火风鼎", "fortune": "吉", "judgment": "鼎，元吉，亨。", "detail": "鼎卦象征鼎立。稳定则成大器。"},
    51: {"name": "震为雷", "fortune": "平", "judgment": "震，亨。震来虩虩，笑言哑哑。震惊百里，不丧匕鬯。", "detail": "震卦主震动。临危不乱则吉。"},
    52: {"name": "艮为山", "fortune": "平", "judgment": "艮，艮其背，不获其身。行其庭，不见其人。无咎。", "detail": "艮卦主停止。当止则止。"},
    53: {"name": "风山渐", "fortune": "吉", "judgment": "渐，女归吉。利贞。", "detail": "渐卦象征渐进。稳步发展则吉。"},
    54: {"name": "雷泽归妹", "fortune": "平", "judgment": "归妹，征凶，无攸利。", "detail": "归妹卦主嫁娶。需正位。"},
    55: {"name": "雷火丰", "fortune": "平", "judgment": "丰，亨。王假之，勿忧，宜日中。", "detail": "丰卦主丰盛。居安思危。"},
    56: {"name": "火山旅", "fortune": "平", "judgment": "旅，小亨。旅贞吉。", "detail": "旅卦象征在外。谨慎守正则吉。"},
    57: {"name": "巽为风", "fortune": "平", "judgment": "巽，小亨。利有攸往，利见大人。", "detail": "巽卦主顺从。柔顺则利。"},
    58: {"name": "兑为泽", "fortune": "吉", "judgment": "兑，亨利贞。", "detail": "兑卦主喜悦。和悦待人则吉。"},
    59: {"name": "风水涣", "fortune": "平", "judgment": "涣，亨。王假有庙。利涉大川，利贞。", "detail": "涣卦主涣散。宜聚合人心。"},
    60: {"name": "水泽节", "fortune": "平", "judgment": "节，亨。苦节不可贞。", "detail": "节卦主节制。适度则吉。"},
    61: {"name": "风泽中孚", "fortune": "吉", "judgment": "中孚，豚鱼吉。利涉大川，利贞。", "detail": "中孚卦主诚信。心诚则灵。"},
    62: {"name": "雷山小过", "fortune": "平", "judgment": "小过，亨利贞。可小事，不可大事。飞鸟遗之音，不宜上，宜下，大吉。", "detail": "小过卦主小有过越。小事可为。"},
    63: {"name": "水火既济", "fortune": "吉", "judgment": "既济，亨。小利贞。初吉终乱。", "detail": "既济卦象征已完成。成功后仍需谨慎。"},
    64: {"name": "火水未济", "fortune": "平", "judgment": "未济，亨。小狐汔济，濡其尾，无攸利。", "detail": "未济象征尚未完成。需继续努力，谨慎收尾。"}
}

TRIGRAMS = ["☰乾", "☱兑", "☲离", "☳震", "☴巽", "☵坎", "☶艮", "☷坤"]


def generate_hexagram(user_input: str):
    seed_str = user_input + datetime.now().strftime("%Y%m%d%H%M%S%f")
    seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    random.seed(seed)
    upper = random.randint(0, 7)
    lower = random.randint(0, 7)
    lines = [random.choice([0, 1]) for _ in range(6)]
    primary_num = (upper * 8) + lower + 1
    return {
        "primary_num": primary_num,
        "primary_name": HEXAGRAMS.get(primary_num, {"name": "未知卦"})["name"],
        "fortune": HEXAGRAMS.get(primary_num, {"fortune": "平"})["fortune"],
        "upper": TRIGRAMS[upper],
        "lower": TRIGRAMS[lower],
        "lines": lines,
        "input": user_input[:60]
    }


def format_hexagram(data):
    lines_str = "\n".join(["— —" if l == 0 else "———" for l in reversed(data["lines"])])
    return f"""🌀 起卦结果

输入：{data['input']}
时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

本卦：{data['primary_name']}（{data['upper']}上 {data['lower']}下）
{lines_str}

吉凶：{data['fortune']}

简解：{HEXAGRAMS.get(data['primary_num'], {}).get('judgment', '宜静观其变，顺势而为。')}"""


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
            [KeyboardButton(text="🌀 起卦")],
            [KeyboardButton(text="返回主菜单")]
        ],
        resize_keyboard=True
    )


def get_rps_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="石头"), KeyboardButton(text="剪刀"), KeyboardButton(text="布")]],
        resize_keyboard=True
    )


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


# ====================== 起卦功能 ======================
@dp.message(lambda m: m.text in ["🌀 起卦", "起卦"])
async def start_divine(message: Message):
    await message.answer(
        "🔮 <b>请输入任意内容起卦</b>\n\n例如：今天运势如何？\n明天适合跳槽吗？",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="返回主菜单")]], resize_keyboard=True)
    )


@dp.message(lambda m: m.text and len(m.text.strip()) >= 2 and m.text.strip() not in ["返回主菜单", "石头", "剪刀", "布", "猜拳", "猜数字", "查询代币", "抽奖", "小游戏", "我的X主页", "设置", "帮助", "全体禁言", "解除禁言", "踢人", "封禁"])
async def process_divine(message: Message):
    text = message.text.strip()
    if text.startswith(('/', '🎟️', '🎮', '🔍')):
        return

    data = generate_hexagram(text)
    result = format_hexagram(data)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 重新起卦", callback_data="re_divine")],
        [InlineKeyboardButton(text="📖 更详细解卦", callback_data=f"detail_{data['primary_num']}")]
    ])

    await message.answer(result, reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == "re_divine")
async def re_divine(callback: CallbackQuery):
    await callback.message.edit_text("🔮 请直接回复任意内容再次起卦～")
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith("detail_"))
async def detail_divine(callback: CallbackQuery):
    num = int(callback.data.split("_")[1])
    info = HEXAGRAMS.get(num, {"name": "未知卦", "judgment": "", "detail": "暂无详细解读", "fortune": "平"})
    text = f"""
📖 第 {num} 卦 · {info['name']}

吉凶：{info['fortune']}
卦辞：{info.get('judgment', '')}

详细解卦：
{info.get('detail', '此卦需结合实际情况灵活解读。')}
    """.strip()
    await callback.message.edit_text(text)
    await callback.answer()


# ====================== 抽奖功能 ======================
class LotteryForm(StatesGroup):
    waiting_name = State()
    waiting_link = State()
    waiting_description = State()
    waiting_prize_type = State()
    waiting_prize_amount = State()
    waiting_winner_count = State()
    waiting_draw_time = State()


@dp.message(lambda m: "抽奖" in m.text)
async def menu_lottery(message: Message, state: FSMContext):
    if not await is_admin(message):
        await message.answer("❌ 权限不足")
        return
    await state.set_state(LotteryForm.waiting_name)
    await message.answer("🎟️ <b>新建抽奖活动</b>\n\n第一步：请输入 <b>活动名称</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="❌ 取消", callback_data="cancel_lottery")]]))


@dp.message(StateFilter(LotteryForm.waiting_name))
async def process_name(message: Message, state: FSMContext):
    if not message.text or not message.text.strip():
        await message.answer("❌ 活动名称不能为空，请重新输入")
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(LotteryForm.waiting_link)
    await message.answer("第二步：请输入 <b>活动链接</b>（可发送 /skip 跳过）")


@dp.message(StateFilter(LotteryForm.waiting_link))
async def process_link(message: Message, state: FSMContext):
    link = "无" if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(link=link)
    await state.set_state(LotteryForm.waiting_description)
    await message.answer("第三步：请输入 <b>活动描述</b>（可发送 /skip 跳过）")


@dp.message(StateFilter(LotteryForm.waiting_description))
async def process_description(message: Message, state: FSMContext):
    desc = "无" if message.text.strip() == "/skip" else message.text.strip()
    await state.update_data(description=desc)
    await state.set_state(LotteryForm.waiting_prize_type)
    await message.answer("第四步：请输入 <b>奖品类型</b>（例如：USDT、NFT）")


@dp.message(StateFilter(LotteryForm.waiting_prize_type))
async def process_prize_type(message: Message, state: FSMContext):
    await state.update_data(prize_type=message.text.strip())
    await state.set_state(LotteryForm.waiting_prize_amount)
    await message.answer("第五步：请输入 <b>奖品数量</b>（例如：100）")


@dp.message(StateFilter(LotteryForm.waiting_prize_amount))
async def process_prize_amount(message: Message, state: FSMContext):
    await state.update_data(prize_amount=message.text.strip())
    await state.set_state(LotteryForm.waiting_winner_count)
    await message.answer("第六步：请输入 <b>中奖人数</b>（例如：5）")


@dp.message(StateFilter(LotteryForm.waiting_winner_count))
async def process_winner_count(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        await state.update_data(winner_count=count)
        await state.set_state(LotteryForm.waiting_draw_time)
        await message.answer("第七步：请输入 <b>开奖时间</b>（例如：2026-04-30 20:00）")
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

    preview = f"🎟️ <b>抽奖活动预览</b>\n\n📌 活动名称：{data['name']}\n🔗 链接：{data.get('link', '无')}\n📝 描述：{data.get('description', '无')}\n🎁 奖品：{data['prize_type']} × {data['prize_amount']}\n👑 中奖人数：{data['winner_count']} 人\n🕒 开奖时间：{message.text}\n\n回复任意消息即可参与！"

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
    text = f"🎉 <b>抽奖活动正式发布！</b>\n\n📌 {state['name']}\n🔗 {state.get('link', '无')}\n📝 {state.get('description', '无')}\n🎁 奖品：{state['prize_type']} × {state['prize_amount']}\n👑 中奖人数：{state['winner_count']} 人\n🕒 开奖时间：{state['draw_time']}\n\n❤️ 回复任意消息即可参与抽奖！\n管理员发送 /draw 开奖"

    await callback.message.edit_text(text)
    await callback.answer("✅ 活动已发布到群里！")


@dp.callback_query(lambda c: c.data == "cancel_lottery")
async def cancel_lottery(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    chat_id = callback.message.chat.id
    lottery_state.pop(chat_id, None)
    await callback.message.edit_text("❌ 抽奖已取消")
    await callback.answer()


@dp.message(lambda m: m.chat.id in lottery_state and not m.text.startswith('/'))
async def lottery_join(message: Message):
    state = lottery_state[message.chat.id]
    if message.from_user.id not in state["participants"]:
        state["participants"].append(message.from_user.id)
        await message.answer(f"✅ 参与成功！当前人数：{len(state['participants'])}", delete_after=8)


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
    mentions = []
    for wid in winners:
        try:
            user = await bot.get_chat(wid)
            name = user.first_name or f"用户{wid}"
            mentions.append(f"<a href='tg://user?id={wid}'>{name}</a>")
        except:
            mentions.append(f"用户{wid}")

    await message.answer(f"🎉 <b>抽奖结果公布</b>\n\n活动：{state['name']}\n奖品：{state['prize_type']} × {state['prize_amount']}\n👑 中奖者：{', '.join(mentions)}\n开奖时间：{state['draw_time']}")
    del lottery_state[message.chat.id]


# ====================== 其他功能 ======================
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
    await message.answer(f"""<b>我的 X 主页</b>
https://x.com/{YOUR_X_USERNAME}

<b>官网</b>
{YOUR_WEBSITE}""")


@dp.message(lambda m: "全体禁言" in m.text)
async def menu_mute(message: Message):
    if not await is_admin(message): return
    muted_chats.add(message.chat.id)
    try:
        await bot.restrict_chat_member(message.chat.id, 0, permissions=ChatPermissions(can_send_messages=False))
        await message.answer("🔇 已开启全体禁言")
    except:
        await message.answer("❌ 操作失败")


@dp.message(lambda m: "解除禁言" in m.text)
async def menu_unmute(message: Message):
    if not await is_admin(message): return
    muted_chats.discard(message.chat.id)
    try:
        await bot.restrict_chat_member(message.chat.id, 0, permissions=ChatPermissions(can_send_messages=True))
        await message.answer("🔊 已解除全体禁言")
    except:
        await message.answer("❌ 操作失败")


@dp.message(Command("kick"))
async def cmd_kick(message: Message):
    if not await is_admin(message) or not message.reply_to_message: return
    user_id = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_id, revoke_messages=False)
        await bot.unban_chat_member(message.chat.id, user_id)
        await message.answer(f"👢 已踢出用户 <code>{user_id}</code>")
    except:
        pass


@dp.message(Command("ban"))
async def cmd_ban(message: Message):
    if not await is_admin(message) or not message.reply_to_message: return
    user_id = message.reply_to_message.from_user.id
    try:
        await bot.ban_chat_member(message.chat.id, user_id)
        await message.answer(f"🚫 已封禁用户 <code>{user_id}</code>")
    except:
        pass


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


# 小游戏
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


@dp.message(lambda m: "返回主菜单" in m.text)
async def back_to_menu(message: Message):
    await message.answer("✅ 已返回主菜单", reply_markup=get_main_menu())


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
