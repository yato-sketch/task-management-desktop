from datetime import datetime
from typing import List, Optional
from models import Task, TaskStatus, TaskFilter, TaskSort, ListTasksOptions
from storage import TaskRepository


class TaskNotFoundError(Exception):
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository
    
    def create_task(self, title: str, description: str = None, due_date: str = None, tags: List[str] = None) -> Task:
        self._validate_create_input(title, description, due_date, tags)
        
        task = Task.create_new(title, description, due_date, tags)
        return self.repository.create(task)
    
    def get_task(self, task_id: str) -> Task:
        self._validate_task_id(task_id)
        
        task = self.repository.find_by_id(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        
        return task
    
    def list_tasks(self, options: ListTasksOptions = None) -> List[Task]:
        if options is None:
            options = ListTasksOptions()
        
        tasks = self.repository.find_all()
        
        if options.filter:
            tasks = self._apply_filters(tasks, options.filter)
        
        if options.sort:
            tasks = self._apply_sorting(tasks, options.sort)
        
        if options.limit and options.limit > 0:
            tasks = tasks[:options.limit]
        
        return tasks
    
    def update_task(self, task_id: str, **updates) -> Task:
        self._validate_task_id(task_id)
        self._validate_update_input(updates)
        
        existing_task = self.repository.find_by_id(task_id)
        if not existing_task:
            raise TaskNotFoundError(task_id)
        
        update_data = {}
        if 'title' in updates and updates['title'] is not None:
            update_data['title'] = updates['title'].strip()
        if 'description' in updates:
            update_data['description'] = updates['description'].strip() if updates['description'] else None
        if 'due_date' in updates:
            update_data['due_date'] = datetime.fromisoformat(updates['due_date']) if updates['due_date'] else None
        if 'tags' in updates:
            update_data['tags'] = [tag.strip() for tag in (updates['tags'] or [])]
        if 'status' in updates and updates['status'] is not None:
            update_data['status'] = updates['status']
        
        return self.repository.update(task_id, update_data)
    
    def complete_task(self, task_id: str) -> Task:
        return self.update_task(task_id, status=TaskStatus.COMPLETED)
    
    def delete_task(self, task_id: str) -> None:
        self._validate_task_id(task_id)
        
        existing_task = self.repository.find_by_id(task_id)
        if not existing_task:
            raise TaskNotFoundError(task_id)
        
        self.repository.delete(task_id)
    
    def _apply_filters(self, tasks: List[Task], filter_obj: TaskFilter) -> List[Task]:
        filtered_tasks = tasks
        
        if filter_obj.status:
            filtered_tasks = [task for task in filtered_tasks if task.status == filter_obj.status]
        
        if filter_obj.tags:
            filtered_tasks = [
                task for task in filtered_tasks
                if any(tag.lower() in [t.lower() for t in task.tags] for tag in filter_obj.tags)
            ]
        
        if filter_obj.search:
            search_term = filter_obj.search.lower().strip()
            if search_term:
                filtered_tasks = [
                    task for task in filtered_tasks
                    if self._matches_search(task, search_term)
                ]
        
        return filtered_tasks
    
    def _matches_search(self, task: Task, search_term: str) -> bool:
        """Enhanced search matching with fuzzy search capabilities"""
        search_words = search_term.split()
        
        # Search in title
        title_matches = self._fuzzy_match(task.title.lower(), search_words)
        
        # Search in description
        desc_matches = False
        if task.description:
            desc_matches = self._fuzzy_match(task.description.lower(), search_words)
        
        # Search in tags
        tag_matches = any(
            self._fuzzy_match(tag.lower(), search_words) 
            for tag in task.tags
        )
        
        return title_matches or desc_matches or tag_matches
    
    def _fuzzy_match(self, text: str, search_words: list) -> bool:
        """Fuzzy matching that handles partial word matches and typos"""
        if not search_words:
            return False
        
        # Check if all search words are found in the text (partial matches allowed)
        for word in search_words:
            if len(word) < 2:  # Skip very short words
                continue
            if not self._contains_word(text, word):
                return False
        return True
    
    def _contains_word(self, text: str, word: str) -> bool:
        """Check if text contains word with fuzzy matching"""
        # Exact match
        if word in text:
            return True
        
        # Partial match - check if any word in text contains the search word
        words_in_text = text.split()
        for text_word in words_in_text:
            if len(word) >= 2 and word in text_word:
                return True
        
        # Fuzzy match for typos (simple implementation)
        if len(word) >= 4:  # Only for words with 4+ characters
            return self._fuzzy_contains(text, word)
        
        return False
    
    def _fuzzy_contains(self, text: str, word: str) -> bool:
        """Simple fuzzy matching for typos"""
        if len(word) < 4:
            return False
        
        # Check if word is contained with 1 character difference
        for i in range(len(text) - len(word) + 1):
            substring = text[i:i+len(word)]
            if self._levenshtein_distance(substring, word) <= 1:
                return True
        
        return False
    
    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def _apply_sorting(self, tasks: List[Task], sort_obj: TaskSort) -> List[Task]:
        def sort_key(task):
            if sort_obj.field == 'title':
                return task.title.lower()
            elif sort_obj.field == 'due_date':
                return task.due_date or datetime.min
            elif sort_obj.field == 'created_at':
                return task.created_at
            elif sort_obj.field == 'status':
                return task.status.value
            else:
                return task.created_at
        
        reverse = sort_obj.direction == 'desc'
        return sorted(tasks, key=sort_key, reverse=reverse)
    
    def _validate_task_id(self, task_id: str):
        if not task_id or not isinstance(task_id, str) or not task_id.strip():
            raise ValueError("Task ID is required and must be a non-empty string")
    
    def _validate_create_input(self, title: str, description: str = None, due_date: str = None, tags: List[str] = None):
        if not title or not isinstance(title, str) or not title.strip():
            raise ValueError("Title is required and must be a non-empty string")
        
        if description is not None and not isinstance(description, str):
            raise ValueError("Description must be a string")
        
        if due_date is not None:
            try:
                datetime.fromisoformat(due_date)
            except ValueError:
                raise ValueError("Due date must be in ISO format (YYYY-MM-DD)")
        
        if tags is not None and not isinstance(tags, list):
            raise ValueError("Tags must be a list of strings")
    
    def _validate_update_input(self, updates: dict):
        if 'title' in updates and updates['title'] is not None:
            if not isinstance(updates['title'], str) or not updates['title'].strip():
                raise ValueError("Title must be a non-empty string")
        
        if 'description' in updates and updates['description'] is not None:
            if not isinstance(updates['description'], str):
                raise ValueError("Description must be a string")
        
        if 'due_date' in updates and updates['due_date'] is not None:
            try:
                datetime.fromisoformat(updates['due_date'])
            except ValueError:
                raise ValueError("Due date must be in ISO format (YYYY-MM-DD)")
        
        if 'tags' in updates and updates['tags'] is not None:
            if not isinstance(updates['tags'], list):
                raise ValueError("Tags must be a list of strings")
        
        if 'status' in updates and updates['status'] is not None:
            if not isinstance(updates['status'], TaskStatus):
                raise ValueError("Status must be a valid TaskStatus")
