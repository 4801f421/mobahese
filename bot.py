from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from handlers import start, handle_surah_selection, handle_ayah_range, handle_voice, handle_pagination
import config

def main():
    updater = Updater(config.API_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(handle_surah_selection, pattern=r"^surah_\d+$"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_ayah_range))
    dp.add_handler(MessageHandler(Filters.voice, handle_voice))
    dp.add_handler(CallbackQueryHandler(handle_pagination, pattern=r"^page_\d+$"))


    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
