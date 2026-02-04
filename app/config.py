"""
Configuration module - loads and validates environment variables.
KHÔNG BAO GIỜ hardcode secrets trong code!
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Config:
    """Application configuration loaded from environment variables."""
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    REPORT_CHAT_ID: int = int(os.getenv('REPORT_CHAT_ID', '0'))
    
    # Google Sheets
    GOOGLE_SHEET_ID: str = os.getenv('GOOGLE_SHEET_ID', '')
    GOOGLE_SHEET_TAB: str = os.getenv('GOOGLE_SHEET_TAB', 'Báo cáo')
    GOOGLE_CREDENTIALS_PATH: str = os.getenv('GOOGLE_CREDENTIALS_PATH', '')
    
    # Timezone
    TZ: str = os.getenv('TZ', 'Asia/Ho_Chi_Minh')
    
    # Cache settings
    CACHE_DURATION: int = int(os.getenv('CACHE_DURATION', '300'))  # 5 minutes default
    
    # Display settings
    MAX_DISPLAY_ITEMS: int = int(os.getenv('MAX_DISPLAY_ITEMS', '10'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that all required configuration is present."""
        errors = []
        
        if not cls.TELEGRAM_BOT_TOKEN:
            errors.append("TELEGRAM_BOT_TOKEN is required")
        
        if not cls.REPORT_CHAT_ID:
            errors.append("REPORT_CHAT_ID is required")
        
        if not cls.GOOGLE_SHEET_ID:
            errors.append("GOOGLE_SHEET_ID is required")
        
        if not cls.GOOGLE_CREDENTIALS_PATH:
            errors.append("GOOGLE_CREDENTIALS_PATH is required")
        elif not Path(cls.GOOGLE_CREDENTIALS_PATH).exists():
            errors.append(f"credentials.json not found at: {cls.GOOGLE_CREDENTIALS_PATH}")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        logger.info("Configuration validated successfully")
        logger.info(f"Target chat ID: {cls.REPORT_CHAT_ID}")
        logger.info(f"Sheet ID: {cls.GOOGLE_SHEET_ID}")
        logger.info(f"Timezone: {cls.TZ}")
        return True


# Export config instance
config = Config()
