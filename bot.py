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

# Store subscribed users (in production, use a database)
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
    "🌅 Every morning brings a new opportunity. Seize it!",
    "📈 Progress is progress, no matter how small. Keep going!",
    "🎨 You are the artist of your own life. Create a masterpiece!"
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
    """Start command handler - subscribe to motivation"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if user_id not in subscribed_users:
        subscribed_users.add(user_id)
        await update.message.reply_text(
            "🌟 *Welcome to Your Motivation Bot!* 🌟\n\n"
            "Your journey to greatness begins now.\n\n"
            "I will send you powerful motivation every 2 hours to keep your fire burning.\n\n"
            "Stay focused. Stay great.\n\n"
            "*Available Commands:*\n"
            "/start - Subscribe to motivation\n"
            "/stop - Unsubscribe from motivation\n"
            "/motivate - Get instant motivation\n"
            "/status - Check your subscription status\n"
            "/help - Show this help message",
            parse_mode='Markdown'
        )
        logger.info(f"New user subscribed: {user_id}")
    else:
        await update.message.reply_text(
            "You're already subscribed! 🚀\n\n"
            "You'll receive motivation every 2 hours.\n"
            "Use /motivate for instant motivation or /stop to unsubscribe."
        )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop command handler - unsubscribe from motivation"""
    user_id = update.effective_user.id
    subscribed_users.discard(user_id)
    await update.message.reply_text(
        "😢 You've been unsubscribed from motivational messages.\n\n"
        "Use /start anytime to resubscribe when you need motivation again! 💪\n\n"
        "Stay great!"
    )
    logger.info(f"User unsubscribed: {user_id}")

async def motivate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send instant motivation message"""
    message = random.choice(MOTIVATIONAL_QUOTES)
    await update.message.reply_text(
        f"💪 *Here's your motivation right now!* 💪\n\n"
        f"{message}\n\n"
        f"Stay focused. Stay great! 🔥",
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check subscription status"""
    user_id = update.effective_user.id
    
    if user_id in subscribed_users:
        await update.message.reply_text(
            "✅ *Active Subscription*\n\n"
            "✓ You are receiving motivational messages every 2 hours\n"
            "✓ Next message will arrive soon\n\n"
            "Use /stop to unsubscribe at any time.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ *Inactive Subscription*\n\n"
            "✗ You are not receiving motivational messages\n\n"
            "Use /start to subscribe and begin your journey to greatness! 🚀",
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command - show all available commands"""
    await update.message.reply_text(
        "🤖 *Motivation Bot Commands* 🤖\n\n"
        "/start - Subscribe to receive motivation every 2 hours\n"
        "/stop - Unsubscribe from motivation messages\n"
        "/motivate - Get an instant motivational quote\n"
        "/status - Check if you're subscribed\n"
        "/help - Show this help message\n\n"
        "*About*\n"
        "I send powerful motivation every 2 hours to keep your fire burning!\n\n"
        "Stay focused. Stay great! 🔥",
        parse_mode='Markdown'
    )

async def post_init(application: Application):
    """Setup scheduler after bot initialization"""
    scheduler = BackgroundScheduler()
    
    async def send_messages():
        await send_motivation(application.bot)
    
    def job_wrapper():
        asyncio.create_task(send_messages())
    
    scheduler.add_job(
        job_wrapper,
        trigger=IntervalTrigger(hours=2),
        id='motivation_job'
    )
    
    scheduler.start()
    logger.info("🚀 Bot started - sending motivation every 2 hours")
    logger.info(f"📊 Commands available: /start, /stop, /motivate, /status, /help")
    logger.info(f"👥 Active subscribers: {len(subscribed_users)}")

def main():
    """Start the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("❌ No bot token found! Set TELEGRAM_BOT_TOKEN environment variable.")
        return
    
    logger.info("🤖 Initializing Motivation Bot...")
    
    # Create application
    application = Application.builder().token(token).post_init(post_init).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("motivate", motivate))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("help", help_command))
    
    # Start the bot
    logger.info("✅ Bot is running and polling for updates...")
    application.run_polling()

if __name__ == '__main__':
    main()
