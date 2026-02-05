"""
Business rules: parsing deadlines, classifying tasks, normalizing text.
"""

import logging
import re
from datetime import date, datetime, timedelta
from typing import Optional
import pytz
from app.config import config
from app.models import Task, TaskStatus

logger = logging.getLogger(__name__)


def get_current_date() -> date:
    """Get current date in configured timezone."""
    tz = pytz.timezone(config.TZ)
    return datetime.now(tz).date()


def parse_deadline(deadline_str: str) -> Optional[date]:
    """
    Parse deadline string to date object.
    Supports:
    - dd/mm/yyyy, d/m/yyyy
    - yyyy-mm-dd
    - Google Sheets serial number (if numeric)
    - datetime objects from API
    
    Returns None if parsing fails.
    """
    if not deadline_str or not deadline_str.strip():
        return None
    
    deadline_str = deadline_str.strip()
    
    # Try dd/mm/yyyy or d/m/yyyy
    patterns = [
        r'^(\d{1,2})/(\d{1,2})/(\d{4})$',  # dd/mm/yyyy
        r'^(\d{4})-(\d{1,2})-(\d{1,2})$',  # yyyy-mm-dd
    ]
    
    for pattern in patterns:
        match = re.match(pattern, deadline_str)
        if match:
            try:
                if pattern.startswith(r'^\d{4}'):  # yyyy-mm-dd
                    year, month, day = match.groups()
                else:  # dd/mm/yyyy
                    day, month, year = match.groups()
                
                return date(int(year), int(month), int(day))
            except (ValueError, TypeError) as e:
                logger.warning(f"Invalid date values in '{deadline_str}': {e}")
                continue
    
    # Try Google Sheets serial number (days since 1899-12-30)
    try:
        serial = float(deadline_str)
        if 1 <= serial <= 100000:  # Reasonable range for dates
            base_date = date(1899, 12, 30)
            result_date = base_date + timedelta(days=int(serial))
            logger.debug(f"Parsed serial number {serial} as {result_date}")
            return result_date
    except (ValueError, TypeError):
        pass
    
    logger.warning(f"Could not parse deadline: '{deadline_str}'")
    return None


def classify_task(task: Task, today: Optional[date] = None) -> Task:
    """
    Classify task based on deadline and current date.
    Updates task.status and task.days_overdue in place.
    
    Args:
        task: Task to classify
        today: Current date (if None, will be computed)
        
    Returns:
        Modified task object
    """
    if today is None:
        today = get_current_date()
    
    # If task is completed, don't classify for alerts
    if task.is_completed:
        task.status = TaskStatus.ON_TRACK  # Just mark as on track
        task.days_overdue = 0
        return task
    
    # If no valid deadline
    if task.deadline is None:
        task.status = TaskStatus.NO_DEADLINE
        task.days_overdue = 0
        return task
    
    # Calculate difference
    delta_days = (task.deadline - today).days
    
    if delta_days < 0:  # Overdue
        task.status = TaskStatus.OVERDUE
        task.days_overdue = abs(delta_days)
    elif delta_days == 0:  # Due today
        task.status = TaskStatus.DUE_TODAY
        task.days_overdue = 0
    elif delta_days == 1:  # Due tomorrow
        task.status = TaskStatus.DUE_TOMORROW
        task.days_overdue = 0
    elif delta_days in [2, 3]:  # Due in 2-3 days
        task.status = TaskStatus.DUE_2_3_DAYS
        task.days_overdue = 0
    else:  # delta_days >= 4
        task.status = TaskStatus.ON_TRACK
        task.days_overdue = 0
    
    return task


def parse_sheet_row(row: list[str], row_index: int) -> Optional[Task]:
    """
    Parse a single row from Google Sheets into a Task object.
    
    Expected columns:
    0: STT
    1: Họ tên
    2: Nội dung công việc đã thực hiện
    3: Mức độ
    4: Deadline
    5: Kết quả / Tiến độ
    6: Ghi chú
    
    Returns None if row is invalid or empty.
    """
    # Skip if row is too short
    if len(row) < 5:  # At minimum need: STT, Họ tên, Nội dung, Mức độ, Deadline
        return None
    
    # Pad row with empty strings if needed
    while len(row) < 8:
        row.append('')
    
    # Skip if essential fields are empty
    ho_ten = row[1].strip()
    noi_dung = row[2].strip()
    
    if not ho_ten and not noi_dung:  # Both empty = skip row
        return None
    
    # Parse deadline
    deadline_raw = row[4].strip() if len(row) > 4 else ''
    deadline = parse_deadline(deadline_raw)
    
    # Parse ngày hoàn thành
    ngay_hoan_thanh_raw = row[6].strip() if len(row) > 6 else ''
    ngay_hoan_thanh = parse_deadline(ngay_hoan_thanh_raw)  # Reuse same parser
    
    # Create task
    task = Task(
        stt=row[0].strip(),
        ho_ten=ho_ten,
        noi_dung=noi_dung,
        muc_do=row[3].strip() if len(row) > 3 else '',
        deadline=deadline,
        deadline_raw=deadline_raw,
        ket_qua=row[5].strip() if len(row) > 5 else '',
        ngay_hoan_thanh=ngay_hoan_thanh,
        ngay_hoan_thanh_raw=ngay_hoan_thanh_raw,
        ghi_chu=row[7].strip() if len(row) > 7 else ''
    )
    
    # Classify task
    classify_task(task)
    
    return task


def parse_all_tasks(data: list[list[str]]) -> list[Task]:
    """
    Parse all rows from Google Sheets data.
    
    Args:
        data: Raw data from Google Sheets (including header row)
        
    Returns:
        List of parsed Task objects
    """
    tasks = []
    
    # Skip header row (index 0)
    for i, row in enumerate(data[1:], start=2):  # Start from row 2
        task = parse_sheet_row(row, i)
        if task:
            tasks.append(task)
    
    logger.info(f"Parsed {len(tasks)} tasks from {len(data)-1} data rows")
    
    # Log statistics
    completed = sum(1 for t in tasks if t.is_completed)
    incomplete = len(tasks) - completed
    logger.info(f"Tasks: {completed} completed, {incomplete} incomplete")
    
    return tasks


def filter_incomplete_tasks(tasks: list[Task]) -> list[Task]:
    """Filter to only incomplete tasks."""
    return [t for t in tasks if not t.is_completed]


def group_tasks_by_status(tasks: list[Task]) -> dict[TaskStatus, list[Task]]:
    """Group tasks by their status."""
    groups: dict[TaskStatus, list[Task]] = {
        TaskStatus.OVERDUE: [],
        TaskStatus.DUE_TODAY: [],
        TaskStatus.DUE_TOMORROW: [],
        TaskStatus.DUE_2_3_DAYS: [],
        TaskStatus.ON_TRACK: [],
        TaskStatus.NO_DEADLINE: []
    }
    
    for task in tasks:
        groups[task.status].append(task)
    
    # Sort overdue by days overdue (descending)
    groups[TaskStatus.OVERDUE].sort(key=lambda t: t.days_overdue, reverse=True)
    
    return groups


def group_tasks_by_person(tasks: list[Task]) -> dict[str, list[Task]]:
    """Group tasks by person (Họ tên)."""
    groups: dict[str, list[Task]] = {}
    
    for task in tasks:
        name = task.ho_ten if task.ho_ten else "Không rõ"
        if name not in groups:
            groups[name] = []
        groups[name].append(task)
    
    return groups


def search_tasks(tasks: list[Task], keyword: str) -> list[Task]:
    """
    Search tasks by keyword in name or content.
    Case-insensitive search.
    """
    keyword_lower = keyword.lower()
    
    return [
        task for task in tasks
        if keyword_lower in task.ho_ten.lower() or keyword_lower in task.noi_dung.lower()
    ]
