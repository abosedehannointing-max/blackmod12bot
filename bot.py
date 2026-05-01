import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import random
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Store subscribed users
subscribed_users = set()

# Motivational quotes
MOTIVATIONAL_QUOTES = [
    "🚀 Your journey to greatness begins now! Keep pushing forward!",
    "💪 The only limit is your mind. Break through it!",
    "✨ Every expert was once a beginner. Keep learning, keep growing!",
    "🔥 Your potential is endless. Don't stop until you're proud!",
    "🎯 Small daily improvements are the key to staggering results.",
    "🌟 You are capable of amazing things. Believe in yourself!",
    "⚡ Success is not final, failure is not fatal. Continue the journey!",
    "💫 Make today so awesome that yesterday gets jealous!",
    "🏆 Winners never quit, and quitters never win. Stay strong!",
    "🌅 Every morning brings a new opportunity. Seize it!"
]

async def send_motivation(context: ContextTypes.DEFAULT_TYPE):
    """Send motivational message to all subscribed users"""
    message = random.choice(MOTIVATIONAL_QUOTES)
    message += "\n\nStay focused. Stay great. 💪"
    
    for user_id in subscribed_users.copy():
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            logger.info(f"Sent motivation to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send to {user_id}: {e}")
            subscribed_users.discard(user_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user_id = update.effective_user.id
    
    if user_id not in subscribed_users:
        subscribed_users.add(user_id)
        await update.message.reply_text(
            "🌟 Your journey to greatness begins now!\n\n"
            "I will send you powerful motivation every 2 hours to keep your fire burning.\n\n"
            "Stay focused. Stay great.\n\n"
            "Use /stop to unsubscribe."
        )
    else:
        await update.message.reply_text("You're already subscribed! 🚀")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop command handler"""
    user_id = update.effective_user.id
    subscribed_users.discard(user_id)
    await update.message.reply_text(
        "You've been unsubscribed. Use /start to resubscribe anytime! 💪"
    )

async def post_init(application: Application):
    """Setup scheduler after bot initialization"""
    scheduler = BackgroundScheduler()
    
    def send_messages():
        asyncio.create_task(send_motivation(application.bot))
    
    scheduler.add_job(
        send_messages,
        trigger=IntervalTrigger(hours=2),
        id='motivation_job'
    )
    
    scheduler.start()
    logger.info("Bot started - sending motivation every 2 hours")

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("No bot token found! Set TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    # Create application
    application = Application.builder().token(token).post_init(post_init).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    
    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
