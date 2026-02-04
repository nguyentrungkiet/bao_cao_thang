"""
Data models for tasks and classifications.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from enum import Enum


class TaskStatus(Enum):
    """Task classification based on deadline."""
    OVERDUE = "overdue"
    DUE_TODAY = "due_today"
    DUE_TOMORROW = "due_tomorrow"
    DUE_2_3_DAYS = "due_2_3_days"
    ON_TRACK = "on_track"
    NO_DEADLINE = "no_deadline"


@dataclass
class Task:
    """Represents a single task from Google Sheets."""
    
    stt: str  # STT (số thứ tự)
    ho_ten: str  # Họ tên
    noi_dung: str  # Nội dung công việc đã thực hiện
    muc_do: str  # Mức độ
    deadline: Optional[date]  # Deadline (parsed)
    deadline_raw: str  # Deadline (raw string from sheet)
    ket_qua: str  # Kết quả / Tiến độ
    ghi_chu: str  # Ghi chú
    
    # Computed fields
    status: TaskStatus = field(default=TaskStatus.NO_DEADLINE)
    days_overdue: int = field(default=0)
    is_completed: bool = field(default=False)
    
    def __post_init__(self):
        """Normalize text fields after initialization."""
        self.ho_ten = self.ho_ten.strip()
        self.noi_dung = self.noi_dung.strip()
        self.muc_do = self.muc_do.strip()
        self.ket_qua = self.ket_qua.strip()
        self.ghi_chu = self.ghi_chu.strip()
        self.deadline_raw = self.deadline_raw.strip()
        
        # Check if completed
        self._check_completion()
    
    def _check_completion(self):
        """Check if task is completed based on 'Kết quả / Tiến độ' column."""
        if not self.ket_qua:
            self.is_completed = False
            return
        
        # Case-insensitive check for "hoàn thành"
        ket_qua_lower = self.ket_qua.lower()
        completion_keywords = ['hoàn thành', 'hoan thanh', 'completed', 'done']
        
        self.is_completed = any(keyword in ket_qua_lower for keyword in completion_keywords)
    
    def __str__(self) -> str:
        """String representation for debugging."""
        return f"Task({self.ho_ten}: {self.noi_dung[:30]}... | Deadline: {self.deadline} | Status: {self.status.value})"


@dataclass
class TasksByPerson:
    """Groups tasks by person for reporting."""
    
    ho_ten: str
    total_tasks: int = 0
    overdue_count: int = 0
    due_soon_count: int = 0  # Due in 1-3 days
    overdue_tasks: list[Task] = field(default_factory=list)
    due_soon_tasks: list[Task] = field(default_factory=list)
    all_tasks: list[Task] = field(default_factory=list)
