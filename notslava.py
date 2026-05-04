# import logging
# import asyncio
# import aiohttp
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.filters import Command
# from aiogram.utils.keyboard import InlineKeyboardBuilder
# from datetime import datetime

# # Sozlamalar
# API_TOKEN = '8639007484:AAGvFLNJiQqkF2Kc5jQ_DM6td4lMM-wMxfg'
# logging.basicConfig(level=logging.INFO)

# bot = Bot(token=API_TOKEN)
# dp = Dispatcher()

# # Ma'lumotlarni xotirada saqlash (Real-time kesh)
# state = {
#     "uzs": 12680.0,
#     "rub": 92.5,
#     "last_updated": None
# }

# async def update_fiat_rates():
#     """Valyuta kurslarini (UZS, RUB) fonda yangilab turish"""
#     url = "https://api.exchangerate-api.com/v4/latest/USD"
#     async with aiohttp.ClientSession() as session:
#         while True:
#             try:
#                 async with session.get(url) as resp:
#                     data = await resp.json()
#                     state["uzs"] = data['rates']['UZS']
#                     state["rub"] = data['rates']['RUB']
#                     state["last_updated"] = datetime.now().strftime("%H:%M:%S")
#                     logging.info(f"Kurslar yangilandi: {state['last_updated']}")
#             except Exception as e:
#                 logging.error(f"Valyuta yangilashda xato: {e}")
            
#             await asyncio.sleep(300) # Har 5 daqiqada fiat kurslarini yangilash

# async def get_bitget_price(symbol: str):
#     """Bitgetdan real-time kripto narxini olish"""
#     url = f"https://api.bitget.com/api/v2/spot/market/tickers?symbol={symbol.upper()}USDT"
#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.get(url) as resp:
#                 res = await resp.json()
#                 if res.get('code') == '00000' and res.get('data'):
#                     ticker = res['data'][0]
#                     return {
#                         "price": float(ticker['lastPr']),
#                         "change": float(ticker['change24h']) * 100
#                     }
#         except Exception as e:
#             logging.error(f"Bitget xatosi: {e}")
#     return None

# @dp.message(F.text)
# async def handle_message(message: types.Message):
#     text = message.text.lower().strip()
#     parts = text.split()
    
#     # 1. UZS kiritsa (masalan: 500000 uzs)
#     if "uzs" in text:
#         try:
#             amount_uzs = float(parts[0])
#             amount_usd = amount_uzs / state["uzs"]
            
#             # Eng mashhur 3 ta koinni real-time olish
#             btc = await get_bitget_price("BTC")
#             ton = await get_bitget_price("TON")
#             eth = await get_bitget_price("ETH")

#             res_text = (
#                 f"🇺🇿 **{amount_uzs:,.0f} UZS**\n\n"
#                 f"🇺🇸 `${amount_usd:,.2f} USD`\n"
#                 f"₿ `{amount_usd / btc['price']:,.6f} BTC`\n"
#                 f"💎 `{amount_usd / ton['price']:,.2f} TON`\n"
#                 f"🔷 `{amount_usd / eth['price']:,.4f} ETH`\n\n"
#                 f"🕒 Kurs vaqti: {state['last_updated']}"
#             )
#             return await message.reply(res_text, parse_mode="Markdown")
#         except:
#             return

#     # 2. Kripto kiritsa (masalan: 1.5 btc yoki 100 ton)
#     try:
#         if len(parts) >= 2:
#             amount = float(parts[0])
#             symbol = parts[1].upper()
#         else:
#             amount = float(parts[0])
#             symbol = "TON"

#         data = await get_bitget_price(symbol)
        
#         if data:
#             total_usd = amount * data['price']
#             total_uzs = total_usd * state["uzs"]
#             total_rub = total_usd * state["rub"]
            
#             sign = "+" if data['change'] > 0 else ""
#             change_text = f"{sign}{data['change']:.2f}%"

#             res_text = (
#                 f"🪙 **{amount:,.2f} {symbol}**\n\n"
#                 f"🇺🇿 `{total_uzs:,.0f} UZS`    | `{change_text}`\n"
#                 f"🇷🇺 `{total_rub:,.0f} RUB`    | `{change_text}`\n"
#                 f"🇺🇸 `{total_usd:,.2f} USD`    \n"
#                 f"🪙 `{amount:,.2f} {symbol}`\n\n"
#                 f"🕒 Real-time: {datetime.now().strftime('%H:%M:%S')}"
#             )
#             await message.reply(res_text, parse_mode="Markdown")
#         else:
#             await message.answer(f"❌ {symbol} topilmadi.")
#     except (ValueError, IndexError):
#         pass

# async def main():
#     # Kurslarni yangilash vazifasini fonda ishga tushirish
#     asyncio.create_task(update_fiat_rates())
#     print("Bot real-time rejimida ishlamoqda...")
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("Bot to'xtatildi")

import logging
import asyncio
import aiohttp
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime

# Sozlamalar
API_TOKEN = '8639007484:AAGvFLNJiQqkF2Kc5jQ_DM6td4lMM-wMxfg'
STARS_RATE = 0.02  # 1 Telegram Stars = 0.02 USD (o'rtacha)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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
                    state["last_updated"] = datetime.now().strftime("%H:%M:%S")
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

@dp.message(F.text)
async def smart_handler(message: types.Message):
    text = message.text.lower().strip()
    
    # 1. "coins" buyrug'i - Asosiy narxlarni chiqarish
    if text == "coins":
        list_coins = ["BTC", "ETH", "TON", "SOL", "NOT"]
        res_text = "📊 **Asosiy Kriptovalyutalar:**\n\n"
        for c in list_coins:
            data = await get_bitget_price(c)
            if data:
                res_text += f"🔹 **{c}**: `${data['price']:,.2f}` ({'+' if data['change'] > 0 else ''}{data['change']:.2f}%)\n"
        return await message.reply(res_text, parse_mode="Markdown")

    # Regex qoliplari
    match_uzs = re.search(r'(\d+[\d.]*)\s*uzs\s*([a-z0-9]+)', text)
    match_pair = re.search(r'(\d+[\d.]*)\s*([a-z0-9]+)\s+([a-z0-9]+)', text)
    match_single = re.search(r'(\d+[\d.]*)\s*([a-z0-9]+)$', text)

    res_text = ""

    # 2. UZS -> Kripto (masalan: 100000 uzs ton)
    if match_uzs:
        amount_uzs = float(match_uzs.group(1))
        symbol = match_uzs.group(2).upper()
        data = await get_bitget_price(symbol)
        if data:
            amount_usd = amount_uzs / state["uzs"]
            crypto_res = amount_usd / data['price']
            res_text = f"💰 **{amount_uzs:,.0f} UZS** ➡️ **{symbol}**\n\n🪙 `{crypto_res:,.6f} {symbol}`\n🇺🇸 `${amount_usd:,.2f} USD`"

    # 3. Juftlik (masalan: 1 btc eth yoki 500 stars ton)
    elif match_pair:
        amount = float(match_pair.group(1))
        from_s = match_pair.group(2).upper()
        to_s = match_pair.group(3).upper()

        # Stars mantiqi
        val_from = STARS_RATE if from_s == "STARS" else (await get_bitget_price(from_s))['price'] if await get_bitget_price(from_s) else None
        val_to = STARS_RATE if to_s == "STARS" else (await get_bitget_price(to_s))['price'] if await get_bitget_price(to_s) else None
        
        if val_from and val_to:
            total_usd = amount * val_from
            converted = total_usd / val_to
            res_text = f"🔄 **{amount:,.0f} {from_s}** ➡️ **{to_s}**\n\n🪙 `{converted:,.6f} {to_s}`\n🇺🇸 `${total_usd:,.2f} USD`"

    # 4. Yakkalik (masalan: 1 btc yoki 100 stars yoki 1 usd)
    elif match_single:
        amount = float(match_single.group(1))
        symbol = match_single.group(2).upper()
        
        # USD o'zini kiritganda
        if symbol == "USD":
            res_text = (f"🇺🇸 **{amount:,.2f} USD**\n\n🇺🇿 `{amount * state['uzs']:,.0f} UZS`\n"
                        f"🇷🇺 `{amount * state['rub']:,.2f} RUB`\n💎 `{(amount / (await get_bitget_price('TON'))['price']):,.2f} TON`")
        
        # Stars o'zini kiritganda
        elif symbol == "STARS":
            total_usd = amount * STARS_RATE
            res_text = (f"⭐ **{amount:,.0f} Stars**\n\n🇺🇸 `${total_usd:,.2f} USD`\n"
                        f"🇺🇿 `{total_usd * state['uzs']:,.0f} UZS`\n🇷🇺 `{total_usd * state['rub']:,.2f} RUB`\n"
                        f"💎 `{(total_usd / (await get_bitget_price('TON'))['price']):,.2f} TON`")
        
        # Kripto o'zini kiritganda
        else:
            data = await get_bitget_price(symbol)
            if data:
                usd_v = amount * data['price']
                res_text = (f"🪙 **{amount:,.2f} {symbol}**\n\n🇺🇿 `{usd_v * state['uzs']:,.0f} UZS`    | `{data['change']:.2f}%`\n"
                            f"🇷🇺 `{usd_v * state['rub']:,.2f} RUB`    | `{data['change']:.2f}%`\n🇺🇸 `${usd_v:,.2f} USD`")

    if res_text:
        kb = InlineKeyboardBuilder().row(types.InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"del_{message.from_user.id}"))
        await message.reply(res_text, parse_mode="Markdown", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("del_"))
async def delete_msg(callback: types.CallbackQuery):
    if callback.from_user.id == int(callback.data.split("_")[1]):
        await callback.message.delete()
    else:
        await callback.answer("Faqat so'rov egasi o'chira oladi!", show_alert=True)

async def main():
    asyncio.create_task(update_fiat_rates())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())