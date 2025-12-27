import os
import asyncio
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from pdf2docx import Converter

# 1. Kalitlarni Render sozlamalaridan xavfsiz o'qish
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# 2. Gemini AI ni sozlash
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 3. Start komandasi
@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.first_name}! 🚀\n\n"
        "Men Diyorbek yaratgan botman.\n"
        "Menga savol yozishingiz yoki rasm yuborishingiz mumkin."
    )

# 4. Savollarga javob berish (Matn va Rasm)
@dp.message()
async def chat_handler(message: types.Message):
    try:
        if message.text:
            response = model.generate_content(message.text)
            await message.answer(response.text)
        elif message.photo:
            await message.answer("Rasmni tahlil qilyapman, kuting...")
            # Bu yerda rasm bilan ishlash kodi bo'ladi
    except Exception as e:
        await message.answer("Xatolik yuz berdi. API kalitni tekshiring.")
        print(f"Xato: {e}")

async def main():
    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
