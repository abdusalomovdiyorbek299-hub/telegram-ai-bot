import os
import asyncio
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile
from pdf2docx import Converter

import os

# Kalitlarni xavfsiz o'qish
BOT_TOKEN = os.getenv("7727293237:AAHv6AkmY25fGg8l7PzvtPLLGowD6HKKnHQ")
GEMINI_KEY = os.getenv("AIzaSyCMN11InEzDquol6RogIXQOi3rdpIASLSM")

# Gemini AI ni sozlash
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. Start komandasi
@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.first_name}! 🚀\n\n"
        "Men Gemini AI asosida ishlaydigan botman.\n"
        "Menga savol yozishingiz, rasm yuborishingiz yoki "
        "PDF faylni Wordga o'tkazish uchun yuborishingiz mumkin."
    )

# 2. Savollarga javob berish (Matn)
@dp.message(F.text)
async def chat_handler(message: types.Message):
    try:
        response = model.generate_content(message.text)
        await message.answer(response.text)
    except Exception as e:
        await message.answer("Xatolik yuz berdi, qaytadan urinib ko'ring.")

# 3. Rasmlarni tahlil qilish
@dp.message(F.photo)
async def photo_handler(message: types.Message):
    await message.answer("Rasmni tahlil qilyapman, kuting...")
    
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    photo_bytes = await bot.download_file(file_info.file_path)
    
    contents = [
        "Ushbu rasmda nima borligini tushuntirib ber yoki undagi matnlarni o'qi.",
        {"mime_type": "image/jpeg", "data": photo_bytes.getvalue()}
    ]
    
    response = model.generate_content(contents)
    await message.answer(response.text)

# 4. PDF ni Wordga o'tkazish
@dp.message(F.document)
async def document_handler(message: types.Message):
    if message.document.file_name.lower().endswith('.pdf'):
        status_msg = await message.answer("Fayl qabul qilindi. Word formatiga o'tkazilyapti...")
        
        file_id = message.document.file_id
        pdf_path = f"{file_id}.pdf"
        docx_path = f"{file_id}.docx"
        
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, pdf_path)
        
        try:
            cv = Converter(pdf_path)
            cv.convert(docx_path, start=0, end=None)
            cv.close()
            
            await bot.send_document(message.chat.id, FSInputFile(docx_path), caption="Tayyor! ✅")
        except Exception as e:
            await message.answer(f"Faylni o'tkazishda xatolik: {e}")
        finally:
            if os.path.exists(pdf_path): os.remove(pdf_path)
            if os.path.exists(docx_path): os.remove(docx_path)
            await status_msg.delete()
    else:
        await message.answer("Iltimos, faqat PDF fayl yuboring.")

async def main():
    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
