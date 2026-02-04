"""
Main entry point for the Telegram Bot.
"""

import logging
import sys
from telegram.ext import Application

from app.config import config
from app.sheets import GoogleSheetsClient
from app.bot import setup_handlers
from app.scheduler import setup_jobs
from app.word_generator import WordReportGenerator

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/bot.log', encoding='utf-8')
    ]
)

# Reduce noise from some libraries
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('telegram').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main():
    """Main function to run the bot."""
    
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed. Please check your .env file.")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Starting Telegram Bot - Work Progress Reporter")
    logger.info("=" * 60)
    
    try:
        # Initialize Google Sheets client
        logger.info("Initializing Google Sheets client...")
        sheets_client = GoogleSheetsClient()
        
        # Initialize Word report generator
        logger.info("Initializing Word report generator...")
        word_generator = WordReportGenerator()
        
        # Test connection by fetching data once
        logger.info("Testing Google Sheets connection...")
        data = sheets_client.fetch_data()
        logger.info(f"Successfully connected to Google Sheets ({len(data)} rows)")
        
        # Create Telegram bot application
        logger.info("Creating Telegram bot application...")
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Store sheets client and word generator in bot_data for access in handlers
        application.bot_data['sheets_client'] = sheets_client
        application.bot_data['word_generator'] = word_generator
        
        # Setup handlers
        logger.info("Setting up bot handlers...")
        setup_handlers(application)
        
        # Setup scheduled jobs
        logger.info("Setting up scheduled jobs...")
        setup_jobs(application)
        
        # Start the bot
        logger.info("=" * 60)
        logger.info("Bot is now running!")
        logger.info(f"Target group chat ID: {config.REPORT_CHAT_ID}")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        # Run the bot until stopped
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Bot stopped.")


if __name__ == "__main__":
    # Import Update here to avoid circular import
    from telegram import Update
    main()
