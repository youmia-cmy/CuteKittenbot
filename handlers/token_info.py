from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import aiohttp

token_router = Router()

@token_router.message(Command("token"))
async def token_info(message: Message):
    if len(message.text.split()) < 2:
        await message.answer("用法：/token <合约地址>\n例如：/token 0x...")
        return
    
    address = message.text.split()[1].strip()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.dexscreener.com/latest/dex/tokens/{address}") as resp:
            if resp.status != 200:
                await message.answer("查询失败，请检查合约地址")
                return
            data = await resp.json()
    
    if not data.get("pairs"):
        await message.answer("未找到该代币的交易对")
        return
    
    pair = data["pairs"][0]
    await message.answer(
        f"🪙 **{pair['baseToken']['name']}** ({pair['baseToken']['symbol']})\n"
        f"价格: ${pair['priceUsd']}\n"
        f"流动性: ${pair['liquidity']['usd']:,.0f}\n"
        f"市值: ${pair['fdv']:,.0f}\n"
        f"链: {pair['chainId']}\n"
        f"DEX: {pair['dexId']}",
        parse_mode="Markdown"
    )
