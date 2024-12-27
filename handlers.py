from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from database import Database
from voice_processing import convert_voice_to_text, compare_texts
import config

db = Database(config.DB_CONFIG)


def generate_page_content(page_number, total_pages, data):
    items_per_page = 10
    start_index = (page_number - 1) * items_per_page
    end_index = start_index + items_per_page
    page_items = data[start_index:end_index]

    page_text = "\n".join([f"{i + 1}. {item}" for i, item in enumerate(page_items)])
    page_text += f"\n\nصفحه {page_number} از {total_pages}"

    keyboard = []
    if page_number > 1:
        keyboard.append(InlineKeyboardButton("صفحه قبل", callback_data=f"page_{page_number - 1}"))
    if page_number < total_pages:
        keyboard.append(InlineKeyboardButton("صفحه بعد", callback_data=f"page_{page_number + 1}"))

    return page_text, InlineKeyboardMarkup([keyboard])


def handle_pagination(update: Update, context: CallbackContext):
    query = update.callback_query
    if not query:
        return

    query.answer()
    callback_data = query.data

    if callback_data.startswith("page_"):
        page_number = int(callback_data.split("_")[1])

        data = context.user_data.get("data", [])
        items_per_page = 5
        total_pages = (len(data) + items_per_page - 1) // items_per_page

        page_text, reply_markup = generate_page_content(page_number, total_pages, data)

        query.edit_message_text(text=page_text, reply_markup=reply_markup)



def start(update: Update, context: CallbackContext):
    # داده‌های نمونه
    data = [f"آیتم {i}" for i in range(1, 31)]
    context.user_data["data"] = data

    # تنظیمات اولیه صفحه‌بندی
    page_number = 1
    items_per_page = 5
    total_pages = (len(data) + items_per_page - 1) // items_per_page

    # تولید صفحه اول
    page_text, reply_markup = generate_page_content(page_number, total_pages, data)

    update.message.reply_text(text=page_text, reply_markup=reply_markup)


def handle_surah_selection(update: Update, context: CallbackContext):
    query = update.callback_query
    surah_id = int(query.data.split("_")[1])
    context.user_data['surah_id'] = surah_id
    query.message.reply_text("محدوده آیه‌ها را وارد کنید (مثلاً 1-10):")

def handle_ayah_range(update: Update, context: CallbackContext):
    text = update.message.text
    try:
        start, end = map(int, text.split("-"))
        surah_id = context.user_data['surah_id']
        ayahs = db.get_ayahs(surah_id, start, end)
        context.user_data['ayahs'] = " ".join(ayahs)
        update.message.reply_text("آیات را بخوانید و وویس خود را ارسال کنید:")
    except ValueError:
        update.message.reply_text("فرمت وارد شده اشتباه است. لطفاً دوباره امتحان کنید.")

def handle_voice(update: Update, context: CallbackContext):
    try:
        voice = update.message.voice.get_file()
        audio_file = voice.download()
        user_text = convert_voice_to_text(audio_file)

        if "خطا" in user_text or "قابل تشخیص نبود" in user_text:
            update.message.reply_text(user_text)
            return

        actual_text = context.user_data.get('ayahs', None)
        if not actual_text:
            update.message.reply_text("متن اصلی یافت نشد. لطفاً دوباره تلاش کنید.")
            return

        errors = compare_texts(user_text, actual_text)
        if errors:
            error_text = "\n".join(
                [f"خطا در کلمه {pos + 1}: متن قرآن '{q_word}' و متن شما '{u_word}'"
                 for pos, q_word, u_word in errors if q_word and u_word]
            )
            update.message.reply_text(f"خطاهای شما:\n{error_text}")
        else:
            update.message.reply_text("متن شما بدون خطا بود. احسنت!")
    except Exception as e:
        update.message.reply_text(f"خطایی رخ داد: {e}")
