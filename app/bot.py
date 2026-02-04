"""
Telegram Bot handlers - commands, menu, conversation.
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)
import pytz

from app.config import config
from app.sheets import GoogleSheetsClient
from app.rules import parse_all_tasks, search_tasks
from app.reporting import (
    build_today_tasks_report, build_overdue_by_person_report,
    build_due_soon_report, build_weekly_report, build_search_results
)
from app.word_generator import WordReportGenerator

logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_KEYWORD = 1


def is_authorized_chat(chat_id: int, allow_private: bool = False) -> bool:
    """
    Check if chat is authorized to use the bot.
    
    Args:
        chat_id: Telegram chat ID
        allow_private: If True, allow private chats for basic commands
    """
    # Always allow in the configured group
    if chat_id == config.REPORT_CHAT_ID:
        return True
    
    # Allow private chats for basic commands if specified
    if allow_private and chat_id > 0:  # Positive IDs are private chats
        return True
    
    return False


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Build the main menu inline keyboard."""
    keyboard = [
        [InlineKeyboardButton("📌 Công việc hôm nay", callback_data="menu_today")],
        [InlineKeyboardButton("⏰ Ai đang trễ deadline", callback_data="menu_overdue")],
        [InlineKeyboardButton("⚠️ Sắp tới hạn (1-3 ngày)", callback_data="menu_due_soon")],
        [InlineKeyboardButton("📊 Báo cáo tuần", callback_data="menu_weekly")],
        [InlineKeyboardButton("🔎 Tìm theo tên/nội dung", callback_data="menu_search")],
        [InlineKeyboardButton("🔄 Làm mới dữ liệu", callback_data="menu_refresh")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_persistent_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build persistent menu keyboard at bottom of chat."""
    keyboard = [
        [KeyboardButton("📌 Hôm nay"), KeyboardButton("⏰ Quá hạn")],
        [KeyboardButton("⚠️ Sắp hạn"), KeyboardButton("📊 Báo cáo tuần")],
        [KeyboardButton("🔎 Tìm kiếm"), KeyboardButton("📄 Menu Word")],
        [KeyboardButton("🔄 Làm mới"), KeyboardButton("ℹ️ Trợ giúp")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)


def get_word_export_menu() -> InlineKeyboardMarkup:
    """Build Word export menu."""
    keyboard = [
        [InlineKeyboardButton("📄 Báo cáo ngày (Word)", callback_data="word_daily")],
        [InlineKeyboardButton("📄 Báo cáo tuần (Word)", callback_data="word_weekly")],
        [InlineKeyboardButton("📄 Quá hạn (Word)", callback_data="word_overdue")],
        [InlineKeyboardButton("↩️ Quay lại", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    chat_id = update.effective_chat.id
    
    # Log chat info for debugging
    logger.info(f"Received /start from chat_id: {chat_id} (configured: {config.REPORT_CHAT_ID})")
    
    if chat_id == config.REPORT_CHAT_ID:
        # In authorized group
        message = (
            "👋 Chào mừng đến với Bot Báo cáo Tiến độ Công việc!\n\n"
            "🤖 Bot này giúp theo dõi và báo cáo tiến độ công việc từ Google Sheets.\n\n"
            "📋 Chức năng:\n"
            "• Báo cáo tự động hàng ngày lúc 06:00\n"
            "• Báo cáo tuần vào thứ Sáu lúc 17:00\n"
            "• Tra cứu công việc theo nhiều tiêu chí\n\n"
            "Sử dụng menu bên dưới hoặc /help để xem hướng dẫn chi tiết."
        )
        await update.message.reply_text(
            message,
            reply_markup=get_persistent_menu_keyboard()
        )
        # Also send inline menu
        await update.message.reply_text(
            "Chọn chức năng:",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # Outside authorized group or in private
        if chat_id > 0:  # Private chat
            message = (
                "👋 Xin chào!\n\n"
                "Bot này chỉ hoạt động trong group Tổ thư ký Viện Công Nghệ Số.\n"
                "Vui lòng sử dụng bot trong group được chỉ định.\n\n"
                "Nếu bạn cần hỗ trợ, vui lòng liên hệ quản trị viên."
            )
        else:  # Other group
            message = (
                "⚠️ Bot chỉ hoạt động trong group Tổ thư ký Viện Công Nghệ Số.\n"
                "Xin lỗi vì sự bất tiện này!"
            )
        await update.message.reply_text(message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "📖 HƯỚNG DẪN SỬ DỤNG BOT\n\n"
        "🤖 LỆNH CƠ BẢN:\n"
        "/start - Hiển thị menu chính\n"
        "/help - Hiển thị hướng dẫn này\n"
        "/ping - Kiểm tra bot hoạt động\n\n"
        "📋 MENU CHỨC NĂNG:\n"
        "📌 Công việc hôm nay - Xem việc cần làm hôm nay + trễ hạn\n"
        "⏰ Ai đang trễ deadline - Thống kê theo người\n"
        "⚠️ Sắp tới hạn - Công việc trong 1-3 ngày tới\n"
        "📊 Báo cáo tuần - Tổng quan tình hình tuần\n"
        "🔎 Tìm kiếm - Tìm theo tên hoặc nội dung\n"
        "🔄 Làm mới - Cập nhật dữ liệu mới nhất\n\n"
        "⏰ BÁO CÁO TỰ ĐỘNG:\n"
        "• Hàng ngày lúc 06:00: Báo cáo tiến độ\n"
        "• Thứ Sáu lúc 17:00: Báo cáo tuần\n\n"
        "📊 PHÂN LOẠI CÔNG VIỆC:\n"
        "🚨 Trễ hạn - Quá deadline\n"
        "⏰ Hôm nay - Phải hoàn thành hôm nay\n"
        "📌 Ngày mai - Deadline vào ngày mai\n"
        "⚠️ Sắp tới - Deadline trong 2-3 ngày\n"
        "✅ Đúng tiến độ - Deadline còn >= 4 ngày\n"
        "❓ Chưa có deadline - Cần bổ sung\n\n"
        "❓ Cần hỗ trợ? Liên hệ quản trị viên."
    )
    await update.message.reply_text(help_text)


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /ping command."""
    tz = pytz.timezone(config.TZ)
    now = datetime.now(tz)
    
    message = (
        f"🏓 Pong!\n\n"
        f"⏰ Thời gian hiện tại ({config.TZ}):\n"
        f"{now.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
        f"✅ Bot đang hoạt động bình thường."
    )
    await update.message.reply_text(message)


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu button callbacks."""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    
    # Check authorization
    if not is_authorized_chat(chat_id):
        await query.edit_message_text(
            "⚠️ Bot chỉ hoạt động trong group Tổ thư ký Viện Công Nghệ Số."
        )
        return
    
    # Get sheets client
    sheets_client: GoogleSheetsClient = context.bot_data['sheets_client']
    
    try:
        callback_data = query.data
        
        if callback_data == "menu_today":
            # Today's tasks
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            message = build_today_tasks_report(tasks)
            await query.edit_message_text(message)
        
        elif callback_data == "menu_overdue":
            # Overdue by person
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            message = build_overdue_by_person_report(tasks)
            await query.edit_message_text(message)
        
        elif callback_data == "menu_due_soon":
            # Due soon (1-3 days)
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            message = build_due_soon_report(tasks)
            await query.edit_message_text(message)
        
        elif callback_data == "menu_weekly":
            # Weekly report
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            message = build_weekly_report(tasks)
            await query.edit_message_text(message)
        
        elif callback_data == "menu_refresh":
            # Refresh data
            sheets_client.invalidate_cache()
            data = sheets_client.fetch_data(force_refresh=True)
            
            tz = pytz.timezone(config.TZ)
            now = datetime.now(tz)
            
            message = (
                f"🔄 Dữ liệu đã được làm mới!\n\n"
                f"⏰ Thời gian: {now.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"📊 Số dòng dữ liệu: {len(data)}\n\n"
                f"✅ Bạn có thể tra cứu dữ liệu mới nhất ngay bây giờ."
            )
            await query.edit_message_text(message)
        
        elif callback_data == "menu_search":
            # Start search conversation
            await query.edit_message_text(
                "🔎 TÌM KIẾM CÔNG VIỆC\n\n"
                "Vui lòng nhập từ khóa để tìm kiếm trong:\n"
                "• Tên người thực hiện\n"
                "• Nội dung công việc\n\n"
                "Gửi /cancel để hủy."
            )
            return WAITING_FOR_KEYWORD
        
        else:
            await query.edit_message_text("❓ Lệnh không xác định.")
    
    except Exception as e:
        logger.error(f"Error in menu callback: {e}", exc_info=True)
        await query.edit_message_text(
            "❌ Đã xảy ra lỗi khi xử lý yêu cầu.\n"
            "Vui lòng thử lại sau hoặc liên hệ quản trị viên."
        )


async def search_keyword_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle keyword input for search."""
    chat_id = update.effective_chat.id
    
    # Check authorization
    if not is_authorized_chat(chat_id):
        await update.message.reply_text(
            "⚠️ Bot chỉ hoạt động trong group Tổ thư ký Viện Công Nghệ Số."
        )
        return ConversationHandler.END
    
    keyword = update.message.text.strip()
    
    if not keyword:
        await update.message.reply_text("❌ Từ khóa không được để trống. Vui lòng thử lại:")
        return WAITING_FOR_KEYWORD
    
    try:
        # Get sheets client
        sheets_client: GoogleSheetsClient = context.bot_data['sheets_client']
        
        # Fetch and search
        data = sheets_client.fetch_data()
        tasks = parse_all_tasks(data)
        results = search_tasks(tasks, keyword)
        
        # Build and send report
        message = build_search_results(results, keyword)
        await update.message.reply_text(message)
        
    except Exception as e:
        logger.error(f"Error in search: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Đã xảy ra lỗi khi tìm kiếm.\n"
            "Vui lòng thử lại sau."
        )
    
    return ConversationHandler.END


async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel search conversation."""
    await update.message.reply_text(
        "❌ Đã hủy tìm kiếm.\n\n"
        "Sử dụng /start để mở menu chính."
    )
    return ConversationHandler.END


async def word_export_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Word export button callbacks."""
    query = update.callback_query
    await query.answer()
    
    chat_id = update.effective_chat.id
    
    # Check authorization
    if not is_authorized_chat(chat_id):
        await query.edit_message_text(
            "⚠️ Bot chỉ hoạt động trong group Tổ thư ký Viện Công Nghệ Số."
        )
        return
    
    # Get sheets client and word generator
    sheets_client: GoogleSheetsClient = context.bot_data['sheets_client']
    word_generator: WordReportGenerator = context.bot_data['word_generator']
    
    try:
        callback_data = query.data
        
        # Notify processing
        await query.edit_message_text("⏳ Đang tạo file Word, vui lòng đợi...")
        
        if callback_data == "word_daily":
            # Generate daily report
            from app.rules import group_tasks_by_status
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            grouped = group_tasks_by_status(tasks)
            
            filepath = word_generator.generate_daily_report(tasks, grouped)
            
            # Send document
            with open(filepath, 'rb') as doc_file:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=doc_file,
                    filename=filepath.name,
                    caption="📄 Báo cáo tiến độ công việc hàng ngày"
                )
            
            await query.edit_message_text(
                "✅ File Word báo cáo ngày đã được gửi!"
            )
        
        elif callback_data == "word_weekly":
            # Generate weekly report
            from app.rules import group_tasks_by_status
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            grouped = group_tasks_by_status(tasks)
            
            filepath = word_generator.generate_weekly_report(tasks, grouped)
            
            # Send document
            with open(filepath, 'rb') as doc_file:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=doc_file,
                    filename=filepath.name,
                    caption="📄 Báo cáo tiến độ công việc tuần"
                )
            
            await query.edit_message_text(
                "✅ File Word báo cáo tuần đã được gửi!"
            )
        
        elif callback_data == "word_overdue":
            # Generate overdue report
            from app.rules import get_overdue_by_person
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            overdue_by_person = get_overdue_by_person(tasks)
            
            filepath = word_generator.generate_overdue_report(overdue_by_person)
            
            # Send document
            with open(filepath, 'rb') as doc_file:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=doc_file,
                    filename=filepath.name,
                    caption="📄 Báo cáo công việc quá hạn"
                )
            
            await query.edit_message_text(
                "✅ File Word báo cáo quá hạn đã được gửi!"
            )
        
        elif callback_data == "back_to_main":
            await query.edit_message_text(
                "Chọn chức năng:",
                reply_markup=get_main_menu_keyboard()
            )
        
    except Exception as e:
        logger.error(f"Error in word export: {e}", exc_info=True)
        await query.edit_message_text(
            "❌ Đã xảy ra lỗi khi tạo file Word.\n"
            "Vui lòng thử lại sau."
        )


async def persistent_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle persistent menu button presses."""
    text = update.message.text
    chat_id = update.effective_chat.id
    
    # Check authorization
    if not is_authorized_chat(chat_id):
        await update.message.reply_text(
            "⚠️ Bot chỉ hoạt động trong group Tổ thư ký Viện Công Nghệ Số."
        )
        return
    
    sheets_client: GoogleSheetsClient = context.bot_data['sheets_client']
    
    try:
        if text == "📌 Hôm nay":
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            message = build_today_tasks_report(tasks)
            await update.message.reply_text(message)
        
        elif text == "⏰ Quá hạn":
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            message = build_overdue_by_person_report(tasks)
            await update.message.reply_text(message)
        
        elif text == "⚠️ Sắp hạn":
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            message = build_due_soon_report(tasks)
            await update.message.reply_text(message)
        
        elif text == "📊 Báo cáo tuần":
            data = sheets_client.fetch_data()
            tasks = parse_all_tasks(data)
            message = build_weekly_report(tasks)
            await update.message.reply_text(message)
        
        elif text == "🔎 Tìm kiếm":
            await update.message.reply_text(
                "🔎 TÌM KIẾM CÔNG VIỆC\n\n"
                "Vui lòng nhập từ khóa để tìm kiếm trong:\n"
                "• Tên người thực hiện\n"
                "• Nội dung công việc\n\n"
                "Gửi /cancel để hủy.",
                reply_markup=get_persistent_menu_keyboard()
            )
            return WAITING_FOR_KEYWORD
        
        elif text == "📄 Menu Word":
            await update.message.reply_text(
                "📄 XUẤT FILE WORD\n\n"
                "Chọn loại báo cáo muốn xuất:",
                reply_markup=get_word_export_menu()
            )
        
        elif text == "🔄 Làm mới":
            sheets_client.invalidate_cache()
            data = sheets_client.fetch_data(force_refresh=True)
            
            tz = pytz.timezone(config.TZ)
            now = datetime.now(tz)
            
            message = (
                f"🔄 Dữ liệu đã được làm mới!\n\n"
                f"⏰ Thời gian: {now.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"📊 Số dòng dữ liệu: {len(data)}\n\n"
                f"✅ Bạn có thể tra cứu dữ liệu mới nhất ngay bây giờ."
            )
            await update.message.reply_text(message)
        
        elif text == "ℹ️ Trợ giúp":
            await help_command(update, context)
    
    except Exception as e:
        logger.error(f"Error in persistent menu: {e}", exc_info=True)
        await update.message.reply_text(
            "❌ Đã xảy ra lỗi khi xử lý yêu cầu.\n"
            "Vui lòng thử lại sau."
        )


def setup_handlers(application):
    """
    Setup all command and callback handlers.
    
    Args:
        application: Telegram Application instance
    """
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping_command))
    
    # Callback query handlers for menus
    application.add_handler(CallbackQueryHandler(
        menu_callback,
        pattern="^menu_(today|overdue|due_soon|weekly|refresh|search)$"
    ))
    
    # Word export callback handlers
    application.add_handler(CallbackQueryHandler(
        word_export_callback,
        pattern="^(word_daily|word_weekly|word_overdue|back_to_main)$"
    ))
    
    # Persistent menu text handler
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex("^(📌 Hôm nay|⏰ Quá hạn|⚠️ Sắp hạn|📊 Báo cáo tuần|🔎 Tìm kiếm|📄 Menu Word|🔄 Làm mới|ℹ️ Trợ giúp)$"),
        persistent_menu_handler
    ))
    
    # Conversation handler for search
    search_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(menu_callback, pattern="^menu_search$"),
            MessageHandler(filters.TEXT & filters.Regex("^🔎 Tìm kiếm$"), persistent_menu_handler)
        ],
        states={
            WAITING_FOR_KEYWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, search_keyword_handler)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel_search)],
        conversation_timeout=120  # 2 minutes timeout
    )
    application.add_handler(search_conv)
    
    logger.info("Bot handlers setup complete")
