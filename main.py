from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import speech_recognition as sr
import difflib
import os


TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
bot = Bot(TOKEN)


def convert_audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ar-SA")
            return text
    except sr.UnknownValueError:
        return "صوت شما قابل تشخیص نبود. لطفاً دوباره تلاش کنید."
    except sr.RequestError as e:
        return f"خطا در برقراری ارتباط با سرویس تشخیص گفتار: {e}"


def compare_texts(user_text, quran_text):
    user_words = user_text.split()
    quran_words = quran_text.split()

    matcher = difflib.SequenceMatcher(None, quran_words, user_words)
    differences = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "replace":
            for i, j in zip(range(i1, i2), range(j1, j2)):
                differences.append((i, quran_words[i], user_words[j]))
        elif tag == "delete":
            for i in range(i1, i2):
                differences.append((i, quran_words[i], None))
        elif tag == "insert":
            for j in range(j1, j2):
                differences.append((None, None, user_words[j]))

    return differences


def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "سلام! این ربات برای مباحثه قرآنی طراحی شده است. لطفاً بخشی از قرآن را انتخاب کرده و وویس خود را ارسال کنید. "
        "توجه: فایل صوتی باید کمتر از 60 ثانیه باشد."
    )


def handle_voice(update: Update, context: CallbackContext):
    user = update.message.from_user
    voice_file = update.message.voice.get_file()
    file_path = f"{user.id}_voice.ogg"

    # دانلود فایل صوتی
    voice_file.download(file_path)

    # تبدیل فایل صوتی به متن
    audio_text = convert_audio_to_text(file_path)

    # متنی که باید مقایسه شود (برای تست: یک نمونه ساده)
    quran_text = "ذلک الکتاب لا ریب فیه"

    # مقایسه متن‌ها
    if audio_text:
        errors = compare_texts(audio_text, quran_text)
        response = f"متن شما: {audio_text}\n\nاختلافات:\n"
        for error in errors:
            response += f"کلمه شماره {error[0]}: {error[1]} - '{error[2]}'\n"

        # ارسال نتیجه
        update.message.reply_text(response)
    else:
        update.message.reply_text("صوت شما قابل پردازش نبود. لطفاً دوباره تلاش کنید.")

    # حذف فایل صوتی
    os.remove(file_path)


def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.voice, handle_voice))

    print("ربات در حال اجرا است...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
