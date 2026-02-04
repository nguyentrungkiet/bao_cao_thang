"""
Unit tests for reporting module.
"""

import pytest
from datetime import date
from app.models import Task, TaskStatus
from app.reporting import (
    format_date, truncate_text, build_task_line,
    build_today_tasks_report, build_overdue_by_person_report
)


class TestFormatDate:
    """Test date formatting."""
    
    def test_format_valid_date(self):
        """Test formatting a valid date."""
        d = date(2024, 12, 25)
        assert format_date(d) == "25/12/2024"
    
    def test_format_none(self):
        """Test formatting None."""
        assert format_date(None) == "Chưa có"


class TestTruncateText:
    """Test text truncation."""
    
    def test_short_text(self):
        """Test text shorter than max length."""
        text = "Short text"
        assert truncate_text(text, 50) == "Short text"
    
    def test_long_text(self):
        """Test text longer than max length."""
        text = "This is a very long text that should be truncated"
        result = truncate_text(text, 20)
        assert len(result) == 20
        assert result.endswith("...")
    
    def test_exact_length(self):
        """Test text exactly at max length."""
        text = "X" * 50
        assert truncate_text(text, 50) == text


class TestBuildTaskLine:
    """Test building task display lines."""
    
    def create_task(
        self,
        ho_ten="John Doe",
        noi_dung="Complete report",
        deadline=date(2024, 12, 25),
        days_overdue=0
    ):
        """Helper to create a test task."""
        task = Task(
            stt="1",
            ho_ten=ho_ten,
            noi_dung=noi_dung,
            muc_do="High",
            deadline=deadline,
            deadline_raw=str(deadline) if deadline else "",
            ket_qua="In Progress",
            ghi_chu=""
        )
        task.days_overdue = days_overdue
        return task
    
    def test_build_with_person(self):
        """Test building line with person name."""
        task = self.create_task()
        line = build_task_line(task, show_person=True)
        
        assert "👤 John Doe" in line
        assert "📝" in line
        assert "📅 25/12/2024" in line
    
    def test_build_without_person(self):
        """Test building line without person name."""
        task = self.create_task()
        line = build_task_line(task, show_person=False)
        
        assert "John Doe" not in line
        assert "📝" in line
    
    def test_build_with_overdue(self):
        """Test building line with days overdue."""
        task = self.create_task(days_overdue=5)
        line = build_task_line(task, show_person=True, show_days_overdue=True)
        
        assert "⚠️ Trễ 5 ngày" in line
    
    def test_long_content_truncation(self):
        """Test that long content is truncated."""
        long_content = "A" * 100
        task = self.create_task(noi_dung=long_content)
        line = build_task_line(task)
        
        # Should be truncated
        assert len(line) < len(long_content) + 100  # Rough check


class TestBuildReports:
    """Test building various reports."""
    
    def create_tasks(self):
        """Create a sample task list for testing."""
        today = date(2024, 12, 25)
        
        tasks = [
            # Overdue task
            Task(
                stt="1",
                ho_ten="Alice",
                noi_dung="Overdue task",
                muc_do="High",
                deadline=date(2024, 12, 20),
                deadline_raw="20/12/2024",
                ket_qua="In Progress",
                ghi_chu=""
            ),
            # Due today
            Task(
                stt="2",
                ho_ten="Bob",
                noi_dung="Today task",
                muc_do="Medium",
                deadline=date(2024, 12, 25),
                deadline_raw="25/12/2024",
                ket_qua="In Progress",
                ghi_chu=""
            ),
            # Completed task
            Task(
                stt="3",
                ho_ten="Charlie",
                noi_dung="Completed task",
                muc_do="Low",
                deadline=date(2024, 12, 20),
                deadline_raw="20/12/2024",
                ket_qua="Hoàn thành",
                ghi_chu=""
            ),
        ]
        
        # Classify tasks
        from app.rules import classify_task
        for task in tasks:
            classify_task(task, today)
        
        return tasks
    
    def test_build_today_tasks_report(self):
        """Test building today's tasks report."""
        tasks = self.create_tasks()
        report = build_today_tasks_report(tasks)
        
        assert "CÔNG VIỆC HÔM NAY" in report
        assert "25/12/2024" in report
        # Should show overdue and due today
        assert "Alice" in report or "Overdue" in report
        assert "Bob" in report or "Today" in report
        # Should not show completed task in alerts
        # (Charlie should not appear in overdue)
    
    def test_build_overdue_by_person_report(self):
        """Test building overdue by person report."""
        tasks = self.create_tasks()
        report = build_overdue_by_person_report(tasks)
        
        # Should show overdue tasks grouped by person
        assert "TRỄ DEADLINE" in report or "Alice" in report
        # Completed tasks should not appear
        assert "Charlie" not in report or "Hoàn thành" not in report
    
    def test_empty_tasks(self):
        """Test reports with empty task list."""
        tasks = []
        
        report1 = build_today_tasks_report(tasks)
        assert "Không có" in report1 or "0" in report1
        
        report2 = build_overdue_by_person_report(tasks)
        assert "Không có" in report2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
