"""
Scheduler module - handles automated daily and weekly reports.
Uses python-telegram-bot's JobQueue for scheduling.
"""

import logging
from datetime import time
import pytz
from telegram.ext import Application
from app.config import config
from app.sheets import GoogleSheetsClient
from app.rules import parse_all_tasks
from app.reporting import build_daily_report, build_weekly_report

logger = logging.getLogger(__name__)


async def send_daily_report(context):
    """Send daily morning report at 6:00 AM."""
    try:
        logger.info("Starting daily report job")
        
        # Get bot and sheets client from context
        sheets_client: GoogleSheetsClient = context.bot_data['sheets_client']
        
        # Fetch data
        data = sheets_client.fetch_data(force_refresh=True)
        tasks = parse_all_tasks(data)
        
        # Build report
        message = build_daily_report(tasks)
        
        # Send to group
        await context.bot.send_message(
            chat_id=config.REPORT_CHAT_ID,
            text=message
        )
        
        logger.info(f"Daily report sent successfully to {config.REPORT_CHAT_ID}")
        
    except Exception as e:
        logger.error(f"Error sending daily report: {e}", exc_info=True)


async def send_weekly_report(context):
    """Send weekly report every Friday at 5:00 PM."""
    try:
        logger.info("Starting weekly report job")
        
        # Get sheets client from context
        sheets_client: GoogleSheetsClient = context.bot_data['sheets_client']
        
        # Fetch data
        data = sheets_client.fetch_data(force_refresh=True)
        tasks = parse_all_tasks(data)
        
        # Build report
        message = build_weekly_report(tasks)
        
        # Send to group
        await context.bot.send_message(
            chat_id=config.REPORT_CHAT_ID,
            text=message
        )
        
        logger.info(f"Weekly report sent successfully to {config.REPORT_CHAT_ID}")
        
    except Exception as e:
        logger.error(f"Error sending weekly report: {e}", exc_info=True)


def setup_jobs(application: Application):
    """
    Setup scheduled jobs using JobQueue.
    
    Args:
        application: Telegram Application instance
    """
    job_queue = application.job_queue
    tz = pytz.timezone(config.TZ)
    
    # Daily report at 6:00 AM (Vietnam time)
    job_queue.run_daily(
        send_daily_report,
        time=time(hour=6, minute=0, tzinfo=tz),
        name='daily_report'
    )
    logger.info("Scheduled daily report at 06:00 (Asia/Ho_Chi_Minh)")
    
    # Weekly report every Friday at 5:00 PM (Vietnam time)
    job_queue.run_daily(
        send_weekly_report,
        time=time(hour=17, minute=0, tzinfo=tz),
        days=(4,),  # Friday is day 4 (Monday=0, Sunday=6)
        name='weekly_report'
    )
    logger.info("Scheduled weekly report on Fridays at 17:00 (Asia/Ho_Chi_Minh)")
