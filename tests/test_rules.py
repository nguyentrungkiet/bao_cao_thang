"""
Unit tests for rules module (deadline parsing and task classification).
"""

import pytest
from datetime import date, timedelta
from app.models import Task, TaskStatus
from app.rules import parse_deadline, classify_task, parse_sheet_row


class TestParseDeadline:
    """Test deadline parsing from various formats."""
    
    def test_parse_dd_mm_yyyy(self):
        """Test dd/mm/yyyy format."""
        assert parse_deadline("25/12/2024") == date(2024, 12, 25)
        assert parse_deadline("01/01/2025") == date(2025, 1, 1)
        assert parse_deadline("5/3/2024") == date(2024, 3, 5)
    
    def test_parse_yyyy_mm_dd(self):
        """Test yyyy-mm-dd format."""
        assert parse_deadline("2024-12-25") == date(2024, 12, 25)
        assert parse_deadline("2025-01-01") == date(2025, 1, 1)
        assert parse_deadline("2024-3-5") == date(2024, 3, 5)
    
    def test_parse_google_serial(self):
        """Test Google Sheets serial number."""
        # Serial 45292 = 2023-12-01
        result = parse_deadline("45292")
        assert result is not None
        assert result.year == 2023
        assert result.month == 12
    
    def test_parse_empty_string(self):
        """Test empty string returns None."""
        assert parse_deadline("") is None
        assert parse_deadline("   ") is None
    
    def test_parse_invalid_format(self):
        """Test invalid format returns None."""
        assert parse_deadline("invalid") is None
        assert parse_deadline("2024/12/25") is None  # Wrong separator
        assert parse_deadline("32/13/2024") is None  # Invalid date
    
    def test_parse_whitespace(self):
        """Test parsing with whitespace."""
        assert parse_deadline("  25/12/2024  ") == date(2024, 12, 25)


class TestClassifyTask:
    """Test task classification based on deadline."""
    
    def create_task(self, deadline: date = None, completed: bool = False):
        """Helper to create a test task."""
        return Task(
            stt="1",
            ho_ten="Test User",
            noi_dung="Test task",
            muc_do="High",
            deadline=deadline,
            deadline_raw=str(deadline) if deadline else "",
            ket_qua="Hoàn thành" if completed else "Đang thực hiện",
            ghi_chu=""
        )
    
    def test_classify_overdue(self):
        """Test OVERDUE classification."""
        today = date(2024, 12, 25)
        task = self.create_task(deadline=date(2024, 12, 20))
        
        classify_task(task, today)
        
        assert task.status == TaskStatus.OVERDUE
        assert task.days_overdue == 5
    
    def test_classify_due_today(self):
        """Test DUE_TODAY classification."""
        today = date(2024, 12, 25)
        task = self.create_task(deadline=date(2024, 12, 25))
        
        classify_task(task, today)
        
        assert task.status == TaskStatus.DUE_TODAY
        assert task.days_overdue == 0
    
    def test_classify_due_tomorrow(self):
        """Test DUE_TOMORROW classification."""
        today = date(2024, 12, 25)
        task = self.create_task(deadline=date(2024, 12, 26))
        
        classify_task(task, today)
        
        assert task.status == TaskStatus.DUE_TOMORROW
        assert task.days_overdue == 0
    
    def test_classify_due_2_3_days(self):
        """Test DUE_2_3_DAYS classification."""
        today = date(2024, 12, 25)
        
        # 2 days
        task1 = self.create_task(deadline=date(2024, 12, 27))
        classify_task(task1, today)
        assert task1.status == TaskStatus.DUE_2_3_DAYS
        
        # 3 days
        task2 = self.create_task(deadline=date(2024, 12, 28))
        classify_task(task2, today)
        assert task2.status == TaskStatus.DUE_2_3_DAYS
    
    def test_classify_on_track(self):
        """Test ON_TRACK classification."""
        today = date(2024, 12, 25)
        task = self.create_task(deadline=date(2024, 12, 30))  # 5 days
        
        classify_task(task, today)
        
        assert task.status == TaskStatus.ON_TRACK
        assert task.days_overdue == 0
    
    def test_classify_no_deadline(self):
        """Test NO_DEADLINE classification."""
        today = date(2024, 12, 25)
        task = self.create_task(deadline=None)
        
        classify_task(task, today)
        
        assert task.status == TaskStatus.NO_DEADLINE
        assert task.days_overdue == 0
    
    def test_classify_completed_task(self):
        """Test that completed tasks are marked as ON_TRACK."""
        today = date(2024, 12, 25)
        task = self.create_task(deadline=date(2024, 12, 20), completed=True)
        
        classify_task(task, today)
        
        # Completed tasks should not be marked as overdue
        assert task.status == TaskStatus.ON_TRACK
        assert task.days_overdue == 0


class TestParseSheetRow:
    """Test parsing Google Sheets rows into Task objects."""
    
    def test_parse_valid_row(self):
        """Test parsing a valid row."""
        row = ["1", "John Doe", "Complete report", "High", "25/12/2024", "In Progress", "Note"]
        
        task = parse_sheet_row(row, 2)
        
        assert task is not None
        assert task.stt == "1"
        assert task.ho_ten == "John Doe"
        assert task.noi_dung == "Complete report"
        assert task.muc_do == "High"
        assert task.deadline == date(2024, 12, 25)
        assert task.ket_qua == "In Progress"
        assert task.ghi_chu == "Note"
    
    def test_parse_short_row(self):
        """Test parsing a row with missing columns."""
        row = ["1", "John Doe", "Complete report", "High", "25/12/2024"]
        
        task = parse_sheet_row(row, 2)
        
        assert task is not None
        assert task.ket_qua == ""
        assert task.ghi_chu == ""
    
    def test_parse_empty_row(self):
        """Test parsing an empty row returns None."""
        row = ["", "", "", "", ""]
        
        task = parse_sheet_row(row, 2)
        
        assert task is None
    
    def test_parse_row_with_whitespace(self):
        """Test parsing row with whitespace."""
        row = ["  1  ", "  John Doe  ", "  Complete report  ", "", ""]
        
        task = parse_sheet_row(row, 2)
        
        assert task is not None
        assert task.stt == "1"
        assert task.ho_ten == "John Doe"
        assert task.noi_dung == "Complete report"
    
    def test_task_completion_detection(self):
        """Test automatic completion detection."""
        # Completed task
        row1 = ["1", "John", "Task", "High", "25/12/2024", "Hoàn thành", ""]
        task1 = parse_sheet_row(row1, 2)
        assert task1.is_completed is True
        
        # In progress task
        row2 = ["2", "Jane", "Task", "High", "25/12/2024", "Đang làm", ""]
        task2 = parse_sheet_row(row2, 2)
        assert task2.is_completed is False
        
        # Case insensitive
        row3 = ["3", "Bob", "Task", "High", "25/12/2024", "HOÀN THÀNH", ""]
        task3 = parse_sheet_row(row3, 2)
        assert task3.is_completed is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
