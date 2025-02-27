import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('BOT_TOKEN')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Check if message contains video
    if message.video:
        file_id = message.video.file_id
    elif message.document and message.document.mime_type.startswith('video/'):
        file_id = message.document.file_id
    else:
        await message.reply_text("Please forward a video file.")
        return

    try:
        # Generate direct download link
        file = await context.bot.get_file(file_id)
        direct_link = f"https://api.telegram.org/file/bot{context.bot.token}/{file.file_path}"
        await message.reply_text(direct_link)
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.reply_text("Failed to generate link.")

async def main():
    # Create Application
    application = Application.builder().token(TOKEN).build()

    # Add handler for forwarded videos
    application.add_handler(MessageHandler(
        filters.FORWARDED & (
            filters.VIDEO | 
            (filters.DOCUMENT & filters.Document.MIME_TYPE.regex(r'^video/.*'))
        , handle_video))

    # Deployment configuration
    if 'HEROKU_APP_NAME' in os.environ:  # Heroku deployment
        app_name = os.environ['HEROKU_APP_NAME']
        port = int(os.environ.get('PORT', 5000))
        await application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TOKEN,
            webhook_url=f"https://{app_name}.herokuapp.com/{TOKEN}"
        )
    else:  # Local/VPS deployment
        await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
