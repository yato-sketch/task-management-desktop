import json
import os
from datetime import datetime
from typing import List, Optional
from models import Task


class TaskRepository:
    def create(self, task: Task) -> Task:
        raise NotImplementedError
    
    def find_by_id(self, task_id: str) -> Optional[Task]:
        raise NotImplementedError
    
    def find_all(self) -> List[Task]:
        raise NotImplementedError
    
    def update(self, task_id: str, updates: dict) -> Task:
        raise NotImplementedError
    
    def delete(self, task_id: str) -> None:
        raise NotImplementedError


class JsonFileTaskRepository(TaskRepository):
    def __init__(self, file_path: str = "tasks.json"):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_tasks(self) -> List[Task]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Task.from_dict(task_data) for task_data in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_tasks(self, tasks: List[Task]):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([task.to_dict() for task in tasks], f, ensure_ascii=False, indent=2)
    
    def create(self, task: Task) -> Task:
        tasks = self._load_tasks()
        tasks.append(task)
        self._save_tasks(tasks)
        return task
    
    def find_by_id(self, task_id: str) -> Optional[Task]:
        tasks = self._load_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None
    
    def find_all(self) -> List[Task]:
        return self._load_tasks()
    
    def update(self, task_id: str, updates: dict) -> Task:
        tasks = self._load_tasks()
        for i, task in enumerate(tasks):
            if task.id == task_id:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                
                task.updated_at = datetime.now()
                tasks[i] = task
                self._save_tasks(tasks)
                return task
        
        raise ValueError(f"Task with ID {task_id} not found")
    
    def delete(self, task_id: str) -> None:
        tasks = self._load_tasks()
        tasks = [task for task in tasks if task.id != task_id]
        self._save_tasks(tasks)
