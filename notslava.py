import logging
import asyncio
import aiohttp
import re
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# Sozlamalar
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
STARS_RATE = 0.02

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Valyuta holati
state = {"uzs": 12800.0, "rub": 95.0, "last_updated": None}

async def update_fiat_rates():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url) as resp:
                    data = await resp.json()
                    state["uzs"] = data['rates']['UZS']
                    state["rub"] = data['rates']['RUB']
            except: pass
            await asyncio.sleep(600)

async def get_bitget_price(symbol: str):
    url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol.upper()}USDT"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                res = await resp.json()
                if res.get('code') == '00000' and res.get('data'):
                    ticker = res['data'][0]
                    return {"price": float(ticker['lastPr']), "change": float(ticker['change24h']) * 100}
        except: return None

def smart_format(value, symbol=""):
    """Mayda va katta sonlarni chiroyli formatlash"""
    symbol = symbol.upper()
    if symbol in ["UZS", "RUB", "USD"]:
        return f"{value:,.2f}".rstrip('0').rstrip('.')
    else:
        # Kriptolar uchun 8 tagacha aniqlik, lekin keraksiz nollarsiz
        return f"{value:,.4f}".rstrip('0').rstrip('.')

@dp.message(F.text)
async def smart_handler(message: types.Message):
    text = message.text.lower().replace(',', '.').strip()
    
    if text == "coins":
        list_coins = ["BTC", "ETH", "TON", "SOL", "NOT"]
        res_text = "📊 **Asosiy Kriptovalyutalar:**\n\n"
        for c in list_coins:
            data = await get_bitget_price(c)
            if data:
                res_text += f"🔹 **{c}**: `${data['price']:,.2f}`\n"
        return await message.reply(res_text, parse_mode="Markdown")

    # Regex: To'liq sonlarni nuqtasi bilan ushlaydi
    num_p = r'(\d+(?:\.\d+)?)'
    
    match_com = re.search(num_p + r'\s*([a-z0-9]+)\s+com\s+' + num_p, text)
    match_uzs = re.search(num_p + r'\s*uzs\s*([a-z0-9]+)', text)
    match_pair = re.search(num_p + r'\s*([a-z0-9]+)\s+([a-z0-9]+)', text)
    match_single = re.search(num_p + r'\s*([a-z0-9]+)$', text)

    res_text = ""

    async def get_val(s):
        s = s.upper()
        if s == "USD": return 1.0
        if s == "STARS": return STARS_RATE
        if s == "UZS": return 1 / state["uzs"]
        if s == "RUB": return 1 / state["rub"]
        d = await get_bitget_price(s)
        return d['price'] if d else None

    # 1. Komissiya hisobi (Masalan: 0.005 btc com 1)
    if match_com:
        amount = float(match_com.group(1))
        symbol = match_com.group(2).upper()
        perc = float(match_com.group(3))
        diff = amount * perc / 100
        result = amount - diff
        rate = await get_val(symbol)
        usd_v = result * rate if rate else 0
        
        res_text = (f"⚖️ **Komissiya: {perc}%**\n\n"
                    f"💰 Jami: `{smart_format(amount, symbol)} {symbol}`\n"
                    f"📉 Ayirma: `{smart_format(diff, symbol)} {symbol}`\n"
                    f"✅ **Qoladi: `{smart_format(result, symbol)} {symbol}`**\n"
                    f"🇺🇸 `${usd_v:,.2f} USD` (Sof)")

    # 2. UZS -> Kripto (Masalan: 500 uzs ton)
    elif match_uzs:
        amount_uzs = float(match_uzs.group(1))
        symbol = match_uzs.group(2).upper()
        price = await get_val(symbol)
        if price:
            amount_usd = amount_uzs / state["uzs"]
            final_crypto = amount_usd / price
            res_text = (f"💰 **{amount_uzs:,.0f} UZS** ➡️ **{symbol}**\n\n"
                        f"🪙 `{smart_format(final_crypto, symbol)} {symbol}`\n"
                        f"🇺🇸 `${amount_usd:,.2f} USD`")

    # 3. Juftlik (Masalan: 0.1 sol eth)
    elif match_pair:
        amount = float(match_pair.group(1))
        f_sym, t_sym = match_pair.group(2).upper(), match_pair.group(3).upper()
        v_from, v_to = await get_val(f_sym), await get_val(t_sym)
        if v_from and v_to:
            total_usd = amount * v_from
            final = total_usd / v_to
            res_text = (f"🔄 **{smart_format(amount, f_sym)} {f_sym}** ➡️ **{t_sym}**\n\n"
                        f"🪙 `{smart_format(final, t_sym)} {t_sym}`\n"
                        f"🇺🇸 `${total_usd:,.2f} USD`")

    # 4. Yakkalik (Masalan: 10 stars)
    elif match_single:
        amount = float(match_single.group(1))
        symbol = match_single.group(2).upper()
        val = await get_val(symbol)
        if val:
            usd_v = amount * val
            ton_data = await get_bitget_price('TON')
            ton_p = ton_data['price'] if ton_data else 1
            res_text = (f"🪙 **{smart_format(amount, symbol)} {symbol}**\n\n"
                        f"🇺🇿 `{usd_v * state['uzs']:,.0f} UZS`\n"
                        f"🇺🇸 `${usd_v:,.2f} USD`\n"
                        f"💎 `{smart_format(usd_v / ton_p, 'TON')} TON`")

    if res_text:
        kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del_{message.from_user.id}"))
        await message.reply(res_text, parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("del_"))
async def delete_msg(callback: types.CallbackQuery):
    if callback.from_user.id == int(callback.data.split("_")[1]):
        await callback.message.delete()
    else:
        await callback.answer("Faqat egasi o'chira oladi!", show_alert=True)

async def main():
    asyncio.create_task(update_fiat_rates())
    # Conflict xatosini oldini olish uchun webhookni tozalash
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
