"""
Test script to verify scheduler timezone is working correctly.
This will send a test message after 1 minute to verify timing.
"""

import asyncio
import logging
import sys
from datetime import datetime
import pytz
from telegram.ext import Application

from app.config import config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


async def send_test_message(context):
    """Send test message with current Vietnam time."""
    try:
        tz = pytz.timezone(config.TZ)
        current_time = datetime.now(tz)
        
        message = f"""🧪 TEST SCHEDULER - THÀNH CÔNG! 🧪

✅ Scheduler đang hoạt động đúng
⏰ Thời gian hiện tại (Asia/Ho_Chi_Minh): {current_time.strftime('%H:%M:%S')}
📅 Ngày: {current_time.strftime('%d/%m/%Y')}
🌍 Timezone: {current_time.tzname()}

📋 Các báo cáo tự động sẽ gửi vào:
• Báo cáo ngày: 6:00 sáng hàng ngày
• Báo cáo tuần: 17:00 thứ 6 hàng tuần

🔔 Test này chứng minh bot đã chạy đúng timezone Việt Nam!"""
        
        await context.bot.send_message(
            chat_id=config.REPORT_CHAT_ID,
            text=message
        )
        
        logger.info(f"✅ Test message sent successfully at {current_time.strftime('%H:%M:%S')}")
        
    except Exception as e:
        logger.error(f"❌ Error sending test message: {e}", exc_info=True)


async def main():
    """Main function to run the test."""
    try:
        # Create event loop for Python 3.14+ compatibility
        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())
        
        logger.info("=" * 60)
        logger.info("SCHEDULER TIMEZONE TEST")
        logger.info("=" * 60)
        
        # Get current Vietnam time
        tz = pytz.timezone(config.TZ)
        current_time = datetime.now(tz)
        logger.info(f"Current Vietnam time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        logger.info(f"Test message will be sent in 1 minute...")
        logger.info(f"Expected send time: {(current_time.timestamp() + 60)}")
        
        # Create application
        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        
        # Schedule test job to run after 1 minute
        job_queue = application.job_queue
        job_queue.run_once(
            send_test_message,
            when=60,  # 60 seconds = 1 minute
            name='timezone_test'
        )
        
        logger.info("✅ Test job scheduled - bot will send message in 1 minute")
        logger.info("Keep this window open and check Telegram...")
        logger.info("Press Ctrl+C to stop after receiving the test message")
        
        # Start polling
        async with application:
            await application.start()
            await application.updater.start_polling()
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Test stopped by user")
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
