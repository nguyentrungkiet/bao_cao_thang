"""
Reporting module - builds formatted messages for Telegram.
"""

import logging
from datetime import date, timedelta
from typing import Optional
from app.config import config
from app.models import Task, TaskStatus, TasksByPerson
from app.rules import get_current_date, group_tasks_by_status, group_tasks_by_person

logger = logging.getLogger(__name__)


def format_date(d: Optional[date]) -> str:
    """Format date for display."""
    if d is None:
        return "Chưa có"
    return d.strftime("%d/%m/%Y")


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text if too long."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def escape_markdown(text: str) -> str:
    """Escape special characters for Telegram MarkdownV2 (if needed)."""
    # For now, just return as-is. Can add escaping if using MarkdownV2
    return text


def build_task_line(task: Task, show_person: bool = True, show_days_overdue: bool = False) -> str:
    """
    Build a single line for a task.
    
    Args:
        task: Task to format
        show_person: Whether to include person name
        show_days_overdue: Whether to show days overdue
    """
    parts = []
    
    if show_person and task.ho_ten:
        parts.append(f"👤 {task.ho_ten}")
    
    # Content (truncated)
    content = truncate_text(task.noi_dung, 60)
    parts.append(f"📝 {content}")
    
    # Deadline
    if task.deadline:
        parts.append(f"📅 {format_date(task.deadline)}")
    
    # Days overdue or completion status
    if task.is_completed and task.ngay_hoan_thanh and task.deadline:
        # For completed tasks, show early/late status
        days_diff = (task.deadline - task.ngay_hoan_thanh).days
        completion_date = format_date(task.ngay_hoan_thanh)
        # Only show early/late if difference is reasonable (within 90 days)
        # Larger differences likely indicate data entry errors
        if abs(days_diff) <= 90:
            if days_diff > 0:
                parts.append(f"✅ Hoàn thành {completion_date} (Sớm {days_diff} ngày)")
            elif days_diff < 0:
                parts.append(f"✅ Hoàn thành {completion_date} (Trễ {abs(days_diff)} ngày)")
            else:
                parts.append(f"✅ Hoàn thành {completion_date} (Đúng hạn)")
        else:
            # Date difference too large - likely data error, just show completion date
            parts.append(f"✅ Hoàn thành {completion_date}")
    elif task.is_completed and task.ngay_hoan_thanh:
        # Has completion date but no deadline
        parts.append(f"✅ Hoàn thành {format_date(task.ngay_hoan_thanh)}")
    elif show_days_overdue and task.days_overdue > 0:
        # For incomplete overdue tasks
        parts.append(f"⚠️ Trễ {task.days_overdue} ngày")
    
    return " | ".join(parts)


def build_daily_report(tasks: list[Task]) -> str:
    """
    Build daily morning report (6:00 AM).
    
    Sections:
    - Summary
    - OVERDUE
    - DUE_TODAY
    - DUE_TOMORROW
    - DUE_2_3_DAYS
    - NO_DEADLINE
    - ON_TRACK (summary only)
    """
    today = get_current_date()
    incomplete_tasks = [t for t in tasks if not t.is_completed]
    groups = group_tasks_by_status(incomplete_tasks)
    
    max_items = config.MAX_DISPLAY_ITEMS
    
    lines = []
    lines.append("=" * 50)
    lines.append("📊 BÁO CÁO TIẾN ĐỘ CÔNG VIỆC HÀNG NGÀY")
    lines.append(f"📅 Ngày: {format_date(today)}")
    lines.append("=" * 50)
    lines.append("")
    
    # Summary
    lines.append(f"📌 Tổng số việc chưa hoàn thành: {len(incomplete_tasks)}")
    lines.append("")
    
    # OVERDUE
    overdue = groups[TaskStatus.OVERDUE]
    if overdue:
        lines.append("🚨 CÔNG VIỆC TRỄ HẠN")
        lines.append(f"   Tổng: {len(overdue)} việc")
        lines.append("")
        for i, task in enumerate(overdue[:max_items], 1):
            lines.append(f"{i}. {build_task_line(task, show_person=True, show_days_overdue=True)}")
        if len(overdue) > max_items:
            lines.append(f"   ... và {len(overdue) - max_items} việc khác")
        lines.append("")
    
    # DUE_TODAY
    due_today = groups[TaskStatus.DUE_TODAY]
    if due_today:
        lines.append("⏰ HÔM NAY PHẢI HOÀN THÀNH")
        lines.append(f"   Tổng: {len(due_today)} việc")
        lines.append("")
        for i, task in enumerate(due_today[:max_items], 1):
            lines.append(f"{i}. {build_task_line(task, show_person=True)}")
        if len(due_today) > max_items:
            lines.append(f"   ... và {len(due_today) - max_items} việc khác")
        lines.append("")
    
    # DUE_TOMORROW
    due_tomorrow = groups[TaskStatus.DUE_TOMORROW]
    if due_tomorrow:
        lines.append("📌 NGÀY MAI PHẢI HOÀN THÀNH")
        lines.append(f"   Tổng: {len(due_tomorrow)} việc")
        lines.append("")
        for i, task in enumerate(due_tomorrow[:max_items], 1):
            lines.append(f"{i}. {build_task_line(task, show_person=True)}")
        if len(due_tomorrow) > max_items:
            lines.append(f"   ... và {len(due_tomorrow) - max_items} việc khác")
        lines.append("")
    
    # DUE_2_3_DAYS
    due_2_3 = groups[TaskStatus.DUE_2_3_DAYS]
    if due_2_3:
        lines.append("⚠️ SẮP TỚI HẠN (2-3 NGÀY)")
        lines.append(f"   Tổng: {len(due_2_3)} việc")
        lines.append("")
        for i, task in enumerate(due_2_3[:max_items], 1):
            lines.append(f"{i}. {build_task_line(task, show_person=True)}")
        if len(due_2_3) > max_items:
            lines.append(f"   ... và {len(due_2_3) - max_items} việc khác")
        lines.append("")
    
    # NO_DEADLINE
    no_deadline = groups[TaskStatus.NO_DEADLINE]
    if no_deadline:
        lines.append("❓ CHƯA CÓ DEADLINE")
        lines.append(f"   Tổng: {len(no_deadline)} việc (cần bổ sung deadline)")
        lines.append("")
        for i, task in enumerate(no_deadline[:5], 1):  # Show fewer
            lines.append(f"{i}. {build_task_line(task, show_person=True)}")
        if len(no_deadline) > 5:
            lines.append(f"   ... và {len(no_deadline) - 5} việc khác")
        lines.append("")
    
    # ON_TRACK (summary only)
    on_track = groups[TaskStatus.ON_TRACK]
    if on_track:
        lines.append(f"✅ Đang đúng tiến độ: {len(on_track)} việc")
        lines.append("")
    
    lines.append("=" * 50)
    lines.append("🤖 Báo cáo tự động từ Telegram Bot")
    
    return "\n".join(lines)


def build_weekly_report(tasks: list[Task]) -> str:
    """
    Build weekly report (Friday 5:00 PM).
    
    Sections:
    - Completed this week
    - Summary
    - Top 10 most overdue tasks
    - Statistics by person
    """
    today = get_current_date()
    
    # Get week start (Monday) and week end (Sunday)
    week_start = today - timedelta(days=today.weekday())  # Monday
    week_end = week_start + timedelta(days=6)  # Sunday
    
    # Filter tasks completed this week
    completed_this_week = [
        t for t in tasks 
        if t.ngay_hoan_thanh and week_start <= t.ngay_hoan_thanh <= week_end
    ]
    
    # Group completed tasks by person
    completed_by_person = {}
    for task in completed_this_week:
        name = task.ho_ten
        if name not in completed_by_person:
            completed_by_person[name] = []
        completed_by_person[name].append(task)
    
    # Get incomplete tasks for current status
    incomplete_tasks = [t for t in tasks if not t.is_completed]
    groups = group_tasks_by_status(incomplete_tasks)
    
    lines = []
    lines.append("=" * 50)
    lines.append("📊 BÁO CÁO TUẦN")
    lines.append(f"📅 Tuần từ {format_date(week_start)} đến {format_date(week_end)}")
    lines.append("=" * 50)
    lines.append("")
    
    # Completed this week summary
    lines.append(f"✅ HOÀN THÀNH TRONG TUẦN: {len(completed_this_week)} việc")
    lines.append("")
    
    if completed_this_week:
        lines.append("👥 Thống kê theo người:")
        for name in sorted(completed_by_person.keys()):
            person_tasks = completed_by_person[name]
            lines.append(f"   👤 {name}: {len(person_tasks)} việc")
            for task in person_tasks[:5]:  # Show first 5
                completion_date = format_date(task.ngay_hoan_thanh) if task.ngay_hoan_thanh else "N/A"
                lines.append(f"      • {task.noi_dung[:50]}... (Hoàn thành: {completion_date})")
            if len(person_tasks) > 5:
                lines.append(f"      ... và {len(person_tasks) - 5} việc khác")
        lines.append("")
    
    # Current status summary
    lines.append(f"📌 TÌNH TRẠNG HIỆN TẠI")
    lines.append(f"   • Chưa hoàn thành: {len(incomplete_tasks)} việc")
    lines.append("")
    
    # Overdue summary
    overdue = groups[TaskStatus.OVERDUE]
    if overdue:
        lines.append("🚨 CÔNG VIỆC TRỄ HẠN")
        lines.append(f"   Tổng: {len(overdue)} việc")
        lines.append("")
        lines.append("   Top 10 việc trễ nhiều nhất:")
        for i, task in enumerate(overdue[:10], 1):
            lines.append(f"   {i}. {build_task_line(task, show_person=True, show_days_overdue=True)}")
        lines.append("")
    
    # Statistics by person for incomplete tasks
    lines.append("👥 THỐNG KÊ CHƯA HOÀN THÀNH THEO NGƯỜI")
    lines.append("")
    
    by_person = group_tasks_by_person(incomplete_tasks)
    
    # Create sorted list of people by total incomplete tasks
    person_stats = []
    for name, person_tasks in by_person.items():
        overdue_count = sum(1 for t in person_tasks if t.status == TaskStatus.OVERDUE)
        due_soon_count = sum(1 for t in person_tasks if t.status in [
            TaskStatus.DUE_TODAY, TaskStatus.DUE_TOMORROW, TaskStatus.DUE_2_3_DAYS
        ])
        person_stats.append({
            'name': name,
            'total': len(person_tasks),
            'overdue': overdue_count,
            'due_soon': due_soon_count
        })
    
    # Sort by overdue count (descending), then by total
    person_stats.sort(key=lambda x: (x['overdue'], x['total']), reverse=True)
    
    for stat in person_stats:
        lines.append(f"👤 {stat['name']}")
        lines.append(f"   • Tổng chưa hoàn thành: {stat['total']}")
        lines.append(f"   • Trễ hạn: {stat['overdue']}")
        lines.append(f"   • Sắp tới hạn (1-3 ngày): {stat['due_soon']}")
        lines.append("")
    
    lines.append("=" * 50)
    lines.append("🤖 Báo cáo tự động từ Telegram Bot")
    
    return "\n".join(lines)


def build_today_tasks_report(tasks: list[Task]) -> str:
    """Build report for 'Công việc hôm nay' button."""
    today = get_current_date()
    incomplete_tasks = [t for t in tasks if not t.is_completed]
    groups = group_tasks_by_status(incomplete_tasks)
    
    lines = []
    lines.append("📌 CÔNG VIỆC HÔM NAY")
    lines.append(f"📅 {format_date(today)}")
    lines.append("")
    
    # Overdue
    overdue = groups[TaskStatus.OVERDUE]
    if overdue:
        lines.append(f"🚨 Trễ hạn: {len(overdue)} việc")
        for i, task in enumerate(overdue[:10], 1):
            lines.append(f"{i}. {build_task_line(task, show_person=True, show_days_overdue=True)}")
        if len(overdue) > 10:
            lines.append(f"... và {len(overdue) - 10} việc khác")
        lines.append("")
    
    # Due today
    due_today = groups[TaskStatus.DUE_TODAY]
    if due_today:
        lines.append(f"⏰ Hôm nay: {len(due_today)} việc")
        for i, task in enumerate(due_today[:10], 1):
            lines.append(f"{i}. {build_task_line(task, show_person=True)}")
        if len(due_today) > 10:
            lines.append(f"... và {len(due_today) - 10} việc khác")
        lines.append("")
    
    # Due tomorrow (optional)
    due_tomorrow = groups[TaskStatus.DUE_TOMORROW]
    if due_tomorrow:
        lines.append(f"📌 Ngày mai: {len(due_tomorrow)} việc")
        for i, task in enumerate(due_tomorrow[:5], 1):
            lines.append(f"{i}. {build_task_line(task, show_person=True)}")
        if len(due_tomorrow) > 5:
            lines.append(f"... và {len(due_tomorrow) - 5} việc khác")
        lines.append("")
    
    if not overdue and not due_today:
        lines.append("✅ Không có việc trễ hạn hoặc đến hạn hôm nay!")
    
    return "\n".join(lines)


def build_overdue_by_person_report(tasks: list[Task]) -> str:
    """Build report for 'Ai đang trễ deadline' button."""
    incomplete_tasks = [t for t in tasks if not t.is_completed]
    overdue_tasks = [t for t in incomplete_tasks if t.status == TaskStatus.OVERDUE]
    
    if not overdue_tasks:
        return "✅ Không có công việc nào trễ hạn!"
    
    lines = []
    lines.append("⏰ AI ĐANG TRỄ DEADLINE")
    lines.append("")
    
    by_person = group_tasks_by_person(overdue_tasks)
    
    # Sort by number of overdue tasks
    sorted_people = sorted(by_person.items(), key=lambda x: len(x[1]), reverse=True)
    
    for name, person_tasks in sorted_people:
        lines.append(f"👤 {name}: {len(person_tasks)} việc trễ")
        for i, task in enumerate(person_tasks[:5], 1):
            lines.append(f"   {i}. {build_task_line(task, show_person=False, show_days_overdue=True)}")
        if len(person_tasks) > 5:
            lines.append(f"   ... và {len(person_tasks) - 5} việc khác")
        lines.append("")
    
    return "\n".join(lines)


def build_due_soon_report(tasks: list[Task]) -> str:
    """Build report for 'Sắp tới hạn' button."""
    incomplete_tasks = [t for t in tasks if not t.is_completed]
    groups = group_tasks_by_status(incomplete_tasks)
    
    lines = []
    lines.append("⚠️ SẮP TỚI HẠN (1-3 NGÀY)")
    lines.append("")
    
    # Due tomorrow
    due_tomorrow = groups[TaskStatus.DUE_TOMORROW]
    if due_tomorrow:
        lines.append(f"📌 Ngày mai: {len(due_tomorrow)} việc")
        for i, task in enumerate(due_tomorrow[:10], 1):
            lines.append(f"{i}. {build_task_line(task, show_person=True)}")
        if len(due_tomorrow) > 10:
            lines.append(f"... và {len(due_tomorrow) - 10} việc khác")
        lines.append("")
    
    # Due in 2-3 days
    due_2_3 = groups[TaskStatus.DUE_2_3_DAYS]
    if due_2_3:
        lines.append(f"📅 2-3 ngày nữa: {len(due_2_3)} việc")
        for i, task in enumerate(due_2_3[:10], 1):
            lines.append(f"{i}. {build_task_line(task, show_person=True)}")
        if len(due_2_3) > 10:
            lines.append(f"... và {len(due_2_3) - 10} việc khác")
        lines.append("")
    
    if not due_tomorrow and not due_2_3:
        lines.append("✅ Không có việc nào sắp tới hạn trong 1-3 ngày!")
    
    return "\n".join(lines)


def build_search_results(tasks: list[Task], keyword: str) -> str:
    """Build report for search results."""
    if not tasks:
        return f"🔍 Không tìm thấy kết quả cho: '{keyword}'"
    
    lines = []
    lines.append(f"🔍 KẾT QUẢ TÌM KIẾM: '{keyword}'")
    lines.append(f"   Tìm thấy: {len(tasks)} việc")
    lines.append("")
    
    for i, task in enumerate(tasks[:15], 1):
        lines.append(f"{i}. {build_task_line(task, show_person=True, show_days_overdue=(task.status == TaskStatus.OVERDUE))}")
        # Only show status for incomplete tasks
        if not task.is_completed and task.status != TaskStatus.NO_DEADLINE:
            status_text = {
                TaskStatus.OVERDUE: "🚨 Trễ hạn",
                TaskStatus.DUE_TODAY: "⏰ Hôm nay",
                TaskStatus.DUE_TOMORROW: "📌 Ngày mai",
                TaskStatus.DUE_2_3_DAYS: "⚠️ Sắp tới",
                TaskStatus.ON_TRACK: "✅ Đúng tiến độ"
            }.get(task.status, "")
            if status_text:
                lines.append(f"   {status_text}")
        lines.append("")
    
    if len(tasks) > 15:
        lines.append(f"... và {len(tasks) - 15} kết quả khác")
    
    return "\n".join(lines)
