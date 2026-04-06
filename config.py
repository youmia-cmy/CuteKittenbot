from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # 多个管理员用逗号分隔

# 欢迎消息模板（支持 HTML）
WELCOME_TEXT = """
🎉 <b>欢迎 {name} 加入群聊！</b> 😺

我是 Cute Kitten 小猫机器人～

📌 请遵守群规：
• 禁止广告、违禁词、刷屏、引战
• 查代币请用 /token 合约地址
• 抽奖请用 /lottery
• 小游戏请用 /game

输入 /help 查看全部功能
玩得开心喵～ 🐱
"""

# 默认违禁词（启动时加载）
DEFAULT_BAD_WORDS = ["spam", "广告", "垃圾", "测试违禁"]
