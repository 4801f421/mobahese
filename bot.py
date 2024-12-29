from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import Database
from datetime import datetime , timezone
from voice_processing import convert_voice_to_text, compare_texts
import config
import os
import uuid
from pydub import AudioSegment

def convert_to_wav(input_file_path):
    try:
        # تولید یک نام یونیک برای فایل جدید
        unique_name = f"{uuid.uuid4()}.wav"
        output_file_path = os.path.join(os.path.dirname(input_file_path), unique_name)
        
        # تبدیل فایل صوتی به فرمت wav
        audio = AudioSegment.from_file(input_file_path)
        audio.export(output_file_path, format="wav")
        
        # حذف فایل اصلی
        os.remove(input_file_path)
        
        # بازگرداندن نام یونیک فایل جدید
        return unique_name
    except Exception as e:
        return f"An error occurred: {e}"


# Initialize database
db = Database(config.DB_CONFIG)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    surahs = db.get_surahs()

    keyboard = []
    for surah in surahs:
        keyboard.append([InlineKeyboardButton(text=f"{surah['name_ar']}", callback_data=f"surah_{surah['number']}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text="سوره مورد نظر را انتخاب کنید :", reply_markup=reply_markup)

# Surah selection handler
async def handle_surah_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    surah_id = int(query.data.split("_")[1])
    context.user_data['surah_id'] = surah_id
    await query.message.reply_text("محدوده آیه‌ها را وارد کنید (مثلاً 1-10):")

# Ayah range handler
async def handle_ayah_range(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        start, end = map(int, text.split("-"))
        surah_id = context.user_data['surah_id']
        ayahs_proc = db.get_ayahs_proc(surah_id, start, end)
        context.user_data['ayahs_proc'] = " ".join(ayahs_proc)
        ayahs = db.get_ayahs(surah_id, start, end)
        context.user_data['ayahs'] = " ".join(ayahs)
        await update.message.reply_text("آیات را بخوانید و وویس خود را ارسال کنید:")
    except :
        await update.message.reply_text("فرمت وارد شده اشتباه است. لطفاً از ابتدا مجددا امتحان کنید.")

# Voice message handler
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = f'{datetime.now(timezone.utc)}.ogg'
    try:
        voice = await update.message.voice.get_file()
        audio_file = await voice.download_to_drive(custom_path=name)
        name = convert_to_wav(name)
        user_text = convert_voice_to_text(name)

        if "خطا" in user_text or "قابل تشخیص نبود" in user_text:
            await update.message.reply_text(user_text)
            return

        actual_text = context.user_data.get('ayahs_proc', None)
        text = context.user_data.get('ayahs', None)
        if not actual_text:
            await update.message.reply_text("متن اصلی یافت نشد. لطفاً دوباره تلاش کنید.")
            return
        
        error_text = ''
        errors = compare_texts(user_text, actual_text)
        if errors:
            for pos, q_word, u_word in errors:
                if pos:
                    if q_word and u_word:
                        error_text += f"خطا در کلمه : {pos + 1} کلمه قرآن : {q_word} و کلمه شما : {u_word} \n"
                    elif q_word:
                        error_text += f"شما کلمه {pos + 1} را جا انداختید . کلمه : {q_word} \n"
                else :
                    error_text += f"شما یک کلمه ی اضافه خواندید : {u_word} \n"
            await update.message.reply_text(f"خطاهای شما:\n\n{error_text}\n\n\nمتن شما:\n{user_text}\n\nمتن قرآن برای بازه مشخص شده:\n{text}")
        else:
            await update.message.reply_text(f"متن شما بدون خطا بود. احسنت!\n\nمتن شما:\n{user_text}\n\nمتن قرآن برای بازه مشخص شده:\n{text}")
    except Exception as e:
        await update.message.reply_text(f"خطایی رخ داد: {e}")

# Main bot setup
def main():
    # Create Application
    application = Application.builder().token(config.API_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_surah_selection, pattern=r"^surah_\d+$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ayah_range))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
#    application.add_handler(CallbackQueryHandler(handle_pagination, pattern=r"^page_\d+$"))

    # Start bot
    application.run_polling()

if __name__ == "__main__":
    main()
