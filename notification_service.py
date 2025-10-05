import threading
import time
from datetime import datetime, timedelta
from plyer import notification
import tkinter as tk
from tkinter import messagebox
from typing import List
from models import Task, TaskStatus
from task_service import TaskService


class NotificationService:
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
        self.running = False
        self.check_interval = 60  # Check every minute
        self.thread = None
        self.notified_tasks = set()
    
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_tasks, daemon=True)
            self.thread.start()
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _monitor_tasks(self):
        while self.running:
            try:
                self._check_due_tasks()
                time.sleep(self.check_interval)
            except Exception as e:
                print(f"Notification service error: {e}")
                time.sleep(5)  # Wait 5 seconds before retrying
    
    def _check_due_tasks(self):
        try:
            tasks = self.task_service.list_tasks()
            now = datetime.now()
            
            for task in tasks:
                if (task.status == TaskStatus.PENDING and 
                    task.due_date and 
                    task.id not in self.notified_tasks):
                    
                    # Check if task is due (within 1 hour of due time)
                    time_diff = task.due_date - now
                    
                    if time_diff <= timedelta(hours=1) and time_diff >= timedelta(minutes=0):
                        self._send_notification(task)
                        self.notified_tasks.add(task.id)
                    
                    # Also notify for overdue tasks
                    elif time_diff < timedelta(minutes=0):
                        self._send_overdue_notification(task)
                        self.notified_tasks.add(task.id)
        
        except Exception as e:
            print(f"Error checking due tasks: {e}")
    
    def _send_notification(self, task: Task):
        try:
            notification.notify(
                title="📝 Task Due Soon!",
                message=f"'{task.title}' is due in {self._format_time_remaining(task.due_date)}",
                timeout=10,
                app_icon=None
            )
        except Exception as e:
            print(f"Failed to send notification: {e}")
    
    def _send_overdue_notification(self, task: Task):
        try:
            notification.notify(
                title="⚠️ Task Overdue!",
                message=f"'{task.title}' was due {self._format_time_past(task.due_date)} ago",
                timeout=10,
                app_icon=None
            )
        except Exception as e:
            print(f"Failed to send overdue notification: {e}")
    
    def _format_time_remaining(self, due_date: datetime) -> str:
        now = datetime.now()
        diff = due_date - now
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
    
    def _format_time_past(self, due_date: datetime) -> str:
        now = datetime.now()
        diff = now - due_date
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''}"
    
    def clear_notifications(self, task_id: str):
        if task_id in self.notified_tasks:
            self.notified_tasks.remove(task_id)
    
    def reset_notifications(self):
        self.notified_tasks.clear()
