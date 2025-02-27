import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('BOT_TOKEN')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        msg = update.message
        if msg.video:
            file_id = msg.video.file_id
        elif msg.document:
            file_id = msg.document.file_id
        else:
            await msg.reply_text("Please forward a video file")
            return

        file = await context.bot.get_file(file_id)
        await msg.reply_text(
            f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}"
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.reply_text("Failed to process video")

def main():
    app = Application.builder().token(TOKEN).build()

    # Corrected document filter
    app.add_handler(MessageHandler(
        filters.FORWARDED & (
            filters.VIDEO | 
            (filters.Document.ALL & filters.Document.MIME_TYPE.regex(r'^video/.*'))
        ,
        handle_video
    ))

    # Webhook configuration
    if 'HEROKU_APP_NAME' in os.environ:
        app_name = os.getenv('HEROKU_APP_NAME')
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.getenv('PORT', 5000)),
            webhook_url=f"https://{app_name}.herokuapp.com/{TOKEN}"
        )
    else:
        app.run_polling()

if __name__ == '__main__':
    main()
