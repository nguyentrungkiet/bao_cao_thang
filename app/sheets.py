"""
Google Sheets client with caching.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
import gspread
from google.oauth2.service_account import Credentials
from app.config import config

logger = logging.getLogger(__name__)


class SheetsCache:
    """Simple in-memory cache for Google Sheets data."""
    
    def __init__(self, duration_seconds: int = 300):
        self.duration = timedelta(seconds=duration_seconds)
        self.data: Optional[list[list[str]]] = None
        self.last_fetch: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if cache is still valid."""
        if self.data is None or self.last_fetch is None:
            return False
        return datetime.now() - self.last_fetch < self.duration
    
    def set(self, data: list[list[str]]):
        """Update cache with new data."""
        self.data = data
        self.last_fetch = datetime.now()
    
    def get(self) -> Optional[list[list[str]]]:
        """Get cached data if valid."""
        if self.is_valid():
            return self.data
        return None
    
    def invalidate(self):
        """Force cache invalidation."""
        self.data = None
        self.last_fetch = None


class GoogleSheetsClient:
    """Client for reading data from Google Sheets."""
    
    def __init__(self):
        self.cache = SheetsCache(duration_seconds=config.CACHE_DURATION)
        self.client: Optional[gspread.Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize gspread client with service account credentials."""
        try:
            # Define the scope
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            
            # Load credentials
            creds = Credentials.from_service_account_file(
                config.GOOGLE_CREDENTIALS_PATH,
                scopes=scopes
            )
            
            # Create client
            self.client = gspread.authorize(creds)
            logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {e}")
            raise
    
    def fetch_data(self, force_refresh: bool = False) -> list[list[str]]:
        """
        Fetch data from Google Sheets with caching.
        
        Args:
            force_refresh: If True, bypass cache and fetch fresh data
            
        Returns:
            List of rows (each row is a list of cell values)
        """
        # Check cache first
        if not force_refresh:
            cached_data = self.cache.get()
            if cached_data is not None:
                logger.info("Using cached data")
                return cached_data
        
        # Fetch fresh data
        try:
            logger.info(f"Fetching data from Google Sheets (Sheet ID: {config.GOOGLE_SHEET_ID})")
            
            # Open the spreadsheet
            spreadsheet = self.client.open_by_key(config.GOOGLE_SHEET_ID)
            
            # Get the specific worksheet
            worksheet = spreadsheet.worksheet(config.GOOGLE_SHEET_TAB)
            
            # Get all values
            data = worksheet.get_all_values()
            
            logger.info(f"Fetched {len(data)} rows from sheet '{config.GOOGLE_SHEET_TAB}'")
            
            # Update cache
            self.cache.set(data)
            
            return data
            
        except gspread.exceptions.WorksheetNotFound:
            logger.error(f"Worksheet '{config.GOOGLE_SHEET_TAB}' not found")
            raise
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"Spreadsheet with ID '{config.GOOGLE_SHEET_ID}' not found")
            raise
        except Exception as e:
            logger.error(f"Error fetching data from Google Sheets: {e}")
            raise
    
    def invalidate_cache(self):
        """Force cache invalidation - use when user requests refresh."""
        logger.info("Cache invalidated")
        self.cache.invalidate()
    
    def get_cache_status(self) -> dict:
        """Get cache status information."""
        return {
            'is_valid': self.cache.is_valid(),
            'last_fetch': self.cache.last_fetch,
            'rows_cached': len(self.cache.data) if self.cache.data else 0
        }
