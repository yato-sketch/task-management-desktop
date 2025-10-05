import customtkinter as ctk
from tkinter import messagebox, simpledialog
from datetime import datetime
from typing import List, Optional
import tkinter as tk
from tkcalendar import DateEntry
import threading

from models import Task, TaskStatus, TaskFilter, TaskSort, ListTasksOptions
from task_service import TaskService
from storage import JsonFileTaskRepository
from notification_service import NotificationService


class TaskManagerApp:
    def __init__(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("Task Manager")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        self.repository = JsonFileTaskRepository()
        self.task_service = TaskService(self.repository)
        self.notification_service = NotificationService(self.task_service)
        
        self.current_filter = TaskFilter()
        self.current_sort = TaskSort()
        
        self.tasks: List[Task] = []
        self.filtered_tasks: List[Task] = []
        
        self.create_widgets()
        self.refresh_task_list()
        self.notification_service.start()
        
        self.root.bind('<Control-n>', lambda e: self.add_task())
        self.root.bind('<F5>', lambda e: self.refresh_task_list())
        self.root.bind('<Delete>', lambda e: self.delete_selected_task())
        self.root.bind('<Return>', lambda e: self.edit_selected_task())
        
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            main_frame, 
            text="📝 Task Manager", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        self.create_control_panel(main_frame)
        self.create_task_list(main_frame)
        self.create_status_bar(main_frame)
    
    def create_control_panel(self, parent):
        control_frame = ctk.CTkFrame(parent)
        control_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        action_frame = ctk.CTkFrame(control_frame)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        add_btn = ctk.CTkButton(
            action_frame,
            text="➕ Add Task",
            command=self.add_task,
            width=120,
            height=35
        )
        add_btn.pack(side="left", padx=(0, 10))
        
        edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Edit",
            command=self.edit_selected_task,
            width=120,
            height=35
        )
        edit_btn.pack(side="left", padx=(0, 10))
        
        complete_btn = ctk.CTkButton(
            action_frame,
            text="✅ Complete",
            command=self.complete_selected_task,
            width=120,
            height=35
        )
        complete_btn.pack(side="left", padx=(0, 10))
        
        delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Delete",
            command=self.delete_selected_task,
            width=120,
            height=35,
            fg_color="#dc3545",
            hover_color="#c82333"
        )
        delete_btn.pack(side="left", padx=(0, 10))
        
        refresh_btn = ctk.CTkButton(
            action_frame,
            text="🔄 Refresh",
            command=self.refresh_task_list,
            width=120,
            height=35
        )
        refresh_btn.pack(side="left", padx=(0, 10))
        
        due_btn = ctk.CTkButton(
            action_frame,
            text="⏰ Due Tasks",
            command=self.show_due_tasks,
            width=120,
            height=35,
            fg_color="#ff9800",
            hover_color="#f57c00"
        )
        due_btn.pack(side="left", padx=(0, 10))
        
        filter_frame = ctk.CTkFrame(control_frame)
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        status_label = ctk.CTkLabel(filter_frame, text="Status:")
        status_label.pack(side="left", padx=(10, 5))
        
        self.status_var = ctk.StringVar(value="all")
        status_combo = ctk.CTkComboBox(
            filter_frame,
            values=["all", "pending", "completed"],
            variable=self.status_var,
            width=120,
            command=self.apply_filters
        )
        status_combo.pack(side="left", padx=(0, 20))
        
        search_label = ctk.CTkLabel(filter_frame, text="Search:")
        search_label.pack(side="left", padx=(10, 5))
        
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            placeholder_text="Search tasks (supports partial matches & typos)...",
            width=250
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        # Search help button
        search_help_btn = ctk.CTkButton(
            filter_frame,
            text="?",
            command=self.show_search_help,
            width=25,
            height=25,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_help_btn.pack(side="left", padx=(0, 10))
        
        tags_label = ctk.CTkLabel(filter_frame, text="Tags:")
        tags_label.pack(side="left", padx=(10, 5))
        
        # Tag selection frame
        tag_frame = ctk.CTkFrame(filter_frame)
        tag_frame.pack(side="left", padx=(0, 10))
        
        self.tags_var = ctk.StringVar()
        self.tags_entry = ctk.CTkEntry(
            tag_frame,
            textvariable=self.tags_var,
            placeholder_text="Type or select tags...",
            width=150
        )
        self.tags_entry.pack(side="left", padx=(5, 5), pady=2)
        self.tags_entry.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        # Tag selector button
        self.tag_selector_btn = ctk.CTkButton(
            tag_frame,
            text="📋",
            command=self.show_tag_selector,
            width=30,
            height=25,
            font=ctk.CTkFont(size=12)
        )
        self.tag_selector_btn.pack(side="left", padx=(0, 5), pady=2)
        
        sort_label = ctk.CTkLabel(filter_frame, text="Sort by:")
        sort_label.pack(side="left", padx=(10, 5))
        
        self.sort_field_var = ctk.StringVar(value="created_at")
        sort_field_combo = ctk.CTkComboBox(
            filter_frame,
            values=["created_at", "title", "due_date", "status"],
            variable=self.sort_field_var,
            width=120,
            command=self.apply_filters
        )
        sort_field_combo.pack(side="left", padx=(0, 5))
        
        self.sort_direction_var = ctk.StringVar(value="desc")
        sort_direction_combo = ctk.CTkComboBox(
            filter_frame,
            values=["desc", "asc"],
            variable=self.sort_direction_var,
            width=80,
            command=self.apply_filters
        )
        sort_direction_combo.pack(side="left", padx=(0, 10))
    
    def create_task_list(self, parent):
        """Create the task list display"""
        # Task list frame
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # List header
        header_frame = ctk.CTkFrame(list_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Header labels
        headers = ["Status", "Title", "Description", "Due Date", "Tags", "Created", "ID"]
        widths = [80, 200, 300, 120, 150, 120, 100]
        
        for i, (header, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(
                header_frame,
                text=header,
                font=ctk.CTkFont(weight="bold"),
                width=width
            )
            label.pack(side="left", padx=2)
        
        # Scrollable frame for tasks
        self.scrollable_frame = ctk.CTkScrollableFrame(list_frame, height=400)
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.task_widgets = []
    
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = ctk.CTkFrame(parent)
        status_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Keyboard shortcuts info
        shortcuts_label = ctk.CTkLabel(
            status_frame,
            text="Shortcuts: Ctrl+N (Add) | F5 (Refresh) | Del (Delete) | Enter (Edit)",
            font=ctk.CTkFont(size=10)
        )
        shortcuts_label.pack(side="right", padx=10, pady=5)
    
    def refresh_task_list(self):
        """Refresh the task list from storage"""
        try:
            # Get all tasks
            self.tasks = self.task_service.list_tasks()
            
            # Apply current filters
            self.apply_filters()
            
            self.update_status(f"Loaded {len(self.tasks)} tasks")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tasks: {str(e)}")
            self.update_status("Error loading tasks")
    
    def apply_filters(self):
        """Apply current filters and refresh the display"""
        try:
            # Build filter
            filter_obj = TaskFilter()
            
            status = self.status_var.get()
            if status != "all":
                filter_obj.status = TaskStatus(status)
            
            search = self.search_var.get().strip()
            if search:
                filter_obj.search = search
            
            tags = self.tags_var.get().strip()
            if tags:
                filter_obj.tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
            
            # Build sort
            sort_obj = TaskSort()
            sort_obj.field = self.sort_field_var.get()
            sort_obj.direction = self.sort_direction_var.get()
            
            # Get filtered tasks
            options = ListTasksOptions(filter=filter_obj, sort=sort_obj)
            self.filtered_tasks = self.task_service.list_tasks(options)
            
            # Update display
            self.update_task_display()
            
            # Show search result info
            search_term = self.search_var.get().strip()
            if search_term:
                self.update_status(f"Found {len(self.filtered_tasks)} of {len(self.tasks)} tasks matching '{search_term}'")
            else:
                self.update_status(f"Showing {len(self.filtered_tasks)} of {len(self.tasks)} tasks")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply filters: {str(e)}")
    
    def update_task_display(self):
        """Update the task list display"""
        # Clear existing widgets
        for widget in self.task_widgets:
            widget.destroy()
        self.task_widgets.clear()
        
        # Create task rows
        for i, task in enumerate(self.filtered_tasks):
            self.create_task_row(task, i)
    
    def create_task_row(self, task: Task, index: int):
        """Create a row widget for a task"""
        row_frame = ctk.CTkFrame(self.scrollable_frame)
        row_frame.pack(fill="x", padx=5, pady=2)
        
        # Status
        status_text = "✅" if task.status == TaskStatus.COMPLETED else "⏳"
        status_label = ctk.CTkLabel(row_frame, text=status_text, width=80)
        status_label.pack(side="left", padx=2)
        
        # Title (truncated)
        title_text = task.title[:30] + "..." if len(task.title) > 30 else task.title
        title_label = ctk.CTkLabel(row_frame, text=title_text, width=200, anchor="w")
        title_label.pack(side="left", padx=2)
        
        # Description (truncated)
        desc_text = task.description[:50] + "..." if task.description and len(task.description) > 50 else (task.description or "-")
        desc_label = ctk.CTkLabel(row_frame, text=desc_text, width=300, anchor="w")
        desc_label.pack(side="left", padx=2)
        
        # Due date
        due_text = task.due_date.strftime("%Y-%m-%d") if task.due_date else "-"
        due_label = ctk.CTkLabel(row_frame, text=due_text, width=120)
        due_label.pack(side="left", padx=2)
        
        # Tags
        tags_text = ", ".join(task.tags[:2]) + ("..." if len(task.tags) > 2 else "")
        tags_text = tags_text or "-"
        tags_label = ctk.CTkLabel(row_frame, text=tags_text, width=150, anchor="w")
        tags_label.pack(side="left", padx=2)
        
        # Created date
        created_text = task.created_at.strftime("%Y-%m-%d")
        created_label = ctk.CTkLabel(row_frame, text=created_text, width=120)
        created_label.pack(side="left", padx=2)
        
        # ID (shortened)
        id_text = task.id[:8] + "..."
        id_label = ctk.CTkLabel(row_frame, text=id_text, width=100)
        id_label.pack(side="left", padx=2)
        
        # Store reference for selection
        row_frame.task = task
        row_frame.index = index
        
        # Bind click events for selection
        for widget in [status_label, title_label, desc_label, due_label, tags_label, created_label, id_label]:
            widget.bind("<Button-1>", lambda e, task=task: self.select_task(task))
        
        self.task_widgets.append(row_frame)
    
    def select_task(self, task: Task):
        """Select a task (highlight it)"""
        # Clear previous selection
        for widget in self.task_widgets:
            widget.configure(fg_color=("gray95", "gray20"))
        
        # Highlight selected task
        for widget in self.task_widgets:
            if hasattr(widget, 'task') and widget.task.id == task.id:
                widget.configure(fg_color=("lightblue", "darkblue"))
                break
        
        self.selected_task = task
    
    def add_task(self):
        """Open add task dialog"""
        dialog = TaskDialog(self.root, "Add Task", self.task_service)
        if dialog.result:
            self.refresh_task_list()
    
    def edit_selected_task(self):
        """Edit the selected task"""
        if not hasattr(self, 'selected_task'):
            messagebox.showwarning("No Selection", "Please select a task to edit")
            return
        
        dialog = TaskDialog(self.root, "Edit Task", self.task_service, self.selected_task)
        if dialog.result:
            self.refresh_task_list()
    
    def complete_selected_task(self):
        """Mark the selected task as completed"""
        if not hasattr(self, 'selected_task'):
            messagebox.showwarning("No Selection", "Please select a task to complete")
            return
        
        try:
            self.task_service.complete_task(self.selected_task.id)
            self.notification_service.clear_notifications(self.selected_task.id)
            self.refresh_task_list()
            messagebox.showinfo("Success", "Task marked as completed")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to complete task: {str(e)}")
    
    def delete_selected_task(self):
        """Delete the selected task"""
        if not hasattr(self, 'selected_task'):
            messagebox.showwarning("No Selection", "Please select a task to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task '{self.selected_task.title}'?"):
            try:
                self.task_service.delete_task(self.selected_task.id)
                self.refresh_task_list()
                messagebox.showinfo("Success", "Task deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete task: {str(e)}")
    
    def update_status(self, message: str):
        self.status_label.configure(text=message)
    
    def show_due_tasks(self):
        try:
            from datetime import datetime, timedelta
            
            now = datetime.now()
            due_tasks = []
            
            for task in self.tasks:
                if (task.status == TaskStatus.PENDING and 
                    task.due_date and 
                    task.due_date <= now + timedelta(hours=24)):
                    due_tasks.append(task)
            
            if not due_tasks:
                messagebox.showinfo("Due Tasks", "No tasks are due in the next 24 hours!")
                return
            
            due_info = "Tasks due in the next 24 hours:\n\n"
            for task in due_tasks:
                time_diff = task.due_date - now
                if time_diff.total_seconds() < 0:
                    due_info += f"⚠️ OVERDUE: {task.title} (was due {abs(time_diff.days)} days ago)\n"
                elif time_diff.total_seconds() < 3600:
                    minutes = int(time_diff.total_seconds() / 60)
                    due_info += f"🔴 Due in {minutes} minutes: {task.title}\n"
                else:
                    hours = int(time_diff.total_seconds() / 3600)
                    due_info += f"🟡 Due in {hours} hours: {task.title}\n"
            
            messagebox.showinfo("Due Tasks", due_info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to check due tasks: {str(e)}")
    
    def show_search_help(self):
        help_text = """🔍 Search Help

The search function supports intelligent matching:

• Partial Matches: "doc" finds "documentation"
• Multiple Words: "meeting team" finds tasks with both words
• Typo Tolerance: "meating" finds "meeting" 
• Search Fields: Title, description, and tags
• Case Insensitive: Works with any capitalization

Examples:
• "urgent" → finds tasks with "urgent" in title/description/tags
• "meeting team" → finds tasks containing both "meeting" and "team"
• "doc" → finds "documentation", "docs", etc.
• "proj" → finds "project", "projects", etc.

Tip: Use shorter, partial words for broader results!"""
        
        messagebox.showinfo("Search Help", help_text)
    
    def clear_all_filters(self):
        """Clear all filters and reset to show all tasks"""
        self.status_var.set("all")
        self.search_var.set("")
        self.tags_var.set("")
        self.sort_field_var.set("created_at")
        self.sort_direction_var.set("desc")
        self.apply_filters()
    
    def get_all_tags(self):
        """Get all unique tags from all tasks"""
        all_tags = set()
        for task in self.tasks:
            all_tags.update(task.tags)
        return sorted(list(all_tags))
    
    def show_tag_selector(self):
        """Show tag selector dialog"""
        all_tags = self.get_all_tags()
        
        if not all_tags:
            messagebox.showinfo("No Tags", "No tags found in any tasks.")
            return
        
        dialog = TagSelectorDialog(self.root, all_tags, self.tags_var.get())
        if dialog.result:
            self.tags_var.set(dialog.result)
            self.apply_filters()
    
    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.notification_service.stop()
    
    def on_closing(self):
        self.notification_service.stop()
        self.root.destroy()


class TaskDialog:
    """Dialog for adding/editing tasks"""
    
    def __init__(self, parent, title: str, task_service: TaskService, task: Task = None):
        self.task_service = task_service
        self.task = task
        self.result = None
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Create widgets first
        self.create_widgets()
        
        # Make sure dialog is visible before grabbing focus
        self.dialog.update_idletasks()
        self.dialog.lift()
        self.dialog.focus_force()
        
        # Try to grab focus, but don't fail if it doesn't work
        try:
            self.dialog.grab_set()
        except:
            pass  # Continue without grab if it fails
        
        # Wait for dialog to close
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Title *", font=ctk.CTkFont(weight="bold"))
        title_label.pack(anchor="w", pady=(0, 5))
        
        self.title_var = ctk.StringVar()
        if self.task:
            self.title_var.set(self.task.title)
        
        title_entry = ctk.CTkEntry(main_frame, textvariable=self.title_var, width=400)
        title_entry.pack(fill="x", pady=(0, 15))
        
        # Description
        desc_label = ctk.CTkLabel(main_frame, text="Description", font=ctk.CTkFont(weight="bold"))
        desc_label.pack(anchor="w", pady=(0, 5))
        
        self.desc_var = ctk.StringVar()
        if self.task and self.task.description:
            self.desc_var.set(self.task.description)
        
        desc_entry = ctk.CTkEntry(main_frame, textvariable=self.desc_var, width=400)
        desc_entry.pack(fill="x", pady=(0, 15))
        
        # Due date
        due_label = ctk.CTkLabel(main_frame, text="Due Date", font=ctk.CTkFont(weight="bold"))
        due_label.pack(anchor="w", pady=(0, 5))
        
        due_frame = ctk.CTkFrame(main_frame)
        due_frame.pack(fill="x", pady=(0, 15))
        
        self.date_picker = DateEntry(
            due_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            font=('Arial', 10)
        )
        self.date_picker.pack(side="left", padx=5, pady=5)
        
        if self.task and self.task.due_date:
            self.date_picker.set_date(self.task.due_date.date())
        
        clear_date_btn = ctk.CTkButton(
            due_frame,
            text="Clear",
            command=self.clear_date,
            width=60,
            height=25
        )
        clear_date_btn.pack(side="left", padx=(10, 0))
        
        # Tags
        tags_label = ctk.CTkLabel(main_frame, text="Tags", font=ctk.CTkFont(weight="bold"))
        tags_label.pack(anchor="w", pady=(0, 5))
        
        # Tags frame
        tags_frame = ctk.CTkFrame(main_frame)
        tags_frame.pack(fill="x", pady=(0, 20))
        
        self.tags_var = ctk.StringVar()
        if self.task and self.task.tags:
            self.tags_var.set(", ".join(self.task.tags))
        
        tags_entry = ctk.CTkEntry(tags_frame, textvariable=self.tags_var, width=300)
        tags_entry.pack(side="left", padx=(5, 5), pady=5)
        
        # Tag selector button for task dialog
        tag_selector_btn = ctk.CTkButton(
            tags_frame,
            text="📋",
            command=self.show_tag_selector_for_task,
            width=30,
            height=25,
            font=ctk.CTkFont(size=12)
        )
        tag_selector_btn.pack(side="left", padx=(0, 5), pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_task,
            width=100
        )
        save_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100
        )
        cancel_btn.pack(side="right")
    
    def clear_date(self):
        self.date_picker.set_date(datetime.now().date())
    
    def show_tag_selector_for_task(self):
        """Show tag selector for task dialog"""
        # Get all tags from the parent app
        parent_app = self.dialog.master
        if hasattr(parent_app, 'get_all_tags'):
            all_tags = parent_app.get_all_tags()
        else:
            all_tags = []
        
        dialog = TagSelectorDialog(self.dialog, all_tags, self.tags_var.get())
        if dialog.result:
            self.tags_var.set(dialog.result)
    
    def save_task(self):
        """Save the task"""
        try:
            title = self.title_var.get().strip()
            if not title:
                messagebox.showerror("Error", "Title is required")
                return
            
            description = self.desc_var.get().strip() or None
            
            # Get date from date picker
            selected_date = self.date_picker.get_date()
            due_date = selected_date.strftime("%Y-%m-%d") if selected_date else None
            
            tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()] if self.tags_var.get().strip() else []
            
            if self.task:
                # Update existing task
                self.task_service.update_task(
                    self.task.id,
                    title=title,
                    description=description,
                    due_date=due_date,
                    tags=tags
                )
            else:
                # Create new task
                self.task_service.create_task(title, description, due_date, tags)
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save task: {str(e)}")
    
    def cancel(self):
        self.dialog.destroy()


class TagSelectorDialog:
    def __init__(self, parent, available_tags, current_tags=""):
        self.available_tags = available_tags
        self.current_tags = current_tags
        self.result = None
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Select Tags")
        self.dialog.geometry("450x600")
        self.dialog.transient(parent)
        
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        self.create_widgets()
        
        self.dialog.update_idletasks()
        self.dialog.lift()
        self.dialog.focus_force()
        
        try:
            self.dialog.grab_set()
        except:
            pass
        
        # Add keyboard shortcuts for the modal
        self.dialog.bind('<Return>', lambda e: self.apply_tags())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        self.dialog.bind('<Control-p>', lambda e: self.preview_selection())
        
        self.dialog.wait_window()
    
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame, 
            text="Select Tags", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(pady=(0, 15))
        
        current_label = ctk.CTkLabel(main_frame, text="Current selection:", font=ctk.CTkFont(weight="bold"))
        current_label.pack(anchor="w", pady=(0, 5))
        
        self.current_var = ctk.StringVar(value=self.current_tags)
        current_entry = ctk.CTkEntry(main_frame, textvariable=self.current_var, width=350)
        current_entry.pack(fill="x", pady=(0, 15))
        
        available_label = ctk.CTkLabel(main_frame, text="Available tags:", font=ctk.CTkFont(weight="bold"))
        available_label.pack(anchor="w", pady=(0, 5))
        
        # Search frame for tags
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", pady=(0, 10))
        
        search_label = ctk.CTkLabel(search_frame, text="Search tags:", font=ctk.CTkFont(size=12))
        search_label.pack(side="left", padx=(10, 5), pady=5)
        
        self.tag_search_var = ctk.StringVar()
        self.tag_search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.tag_search_var,
            placeholder_text="Type to filter tags...",
            width=200
        )
        self.tag_search_entry.pack(side="left", padx=(0, 10), pady=5)
        self.tag_search_entry.bind('<KeyRelease>', lambda e: self.filter_tags())
        
        clear_search_btn = ctk.CTkButton(
            search_frame,
            text="Clear",
            command=self.clear_tag_search,
            width=60,
            height=25
        )
        clear_search_btn.pack(side="left", padx=(0, 10), pady=5)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(main_frame, height=250)
        self.scrollable_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Create a frame for the tag grid
        self.tag_grid_frame = ctk.CTkFrame(self.scrollable_frame)
        self.tag_grid_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tag_buttons = []
        self.create_tag_grid()
        
        # Initialize selected tags from current_tags
        self.initialize_selected_tags()
        
        action_frame = ctk.CTkFrame(main_frame)
        action_frame.pack(fill="x", pady=(10, 0))
        
        select_all_btn = ctk.CTkButton(
            action_frame,
            text="Select All",
            command=self.select_all_tags,
            width=100
        )
        select_all_btn.pack(side="left", padx=(0, 10))
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="Clear All",
            command=self.clear_all_tags,
            width=80,
            fg_color="#f44336",
            hover_color="#d32f2f"
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
        preview_btn = ctk.CTkButton(
            button_frame,
            text="Preview",
            command=self.preview_selection,
            width=80,
            fg_color="#FF9800",
            hover_color="#F57C00"
        )
        preview_btn.pack(side="right", padx=(10, 0))
        
        apply_btn = ctk.CTkButton(
            button_frame,
            text="Apply & Find",
            command=self.apply_tags,
            width=120,
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        apply_btn.pack(side="right", padx=(10, 0))
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel,
            width=100
        )
        cancel_btn.pack(side="right")
        
        self.update_selection()
    
    def create_tag_grid(self):
        """Create a grid layout for tags that wraps properly"""
        # Calculate number of columns based on available width
        # Assuming each button is about 120px wide with 10px padding
        button_width = 120
        padding = 10
        available_width = 350  # Approximate width of the scrollable frame
        
        cols = max(1, available_width // (button_width + padding))
        
        row = 0
        col = 0
        
        for tag in self.available_tags:
            btn = ctk.CTkButton(
                self.tag_grid_frame,
                text=tag,
                command=lambda t=tag: self.toggle_tag(t),
                width=button_width,
                height=30
            )
            btn.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
            btn.tag = tag
            btn.selected = False
            self.tag_buttons.append(btn)
            
            col += 1
            if col >= cols:
                col = 0
                row += 1
        
        # Configure grid weights for proper resizing
        for i in range(cols):
            self.tag_grid_frame.grid_columnconfigure(i, weight=1)
    
    def create_tag_button(self, tag):
        """Legacy method - now handled by create_tag_grid"""
        pass
    
    def initialize_selected_tags(self):
        """Initialize selected tags from current_tags string"""
        if not self.current_tags:
            return
        
        # Parse current tags (comma-separated)
        selected_tags = [tag.strip() for tag in self.current_tags.split(",") if tag.strip()]
        
        # Mark corresponding buttons as selected
        for btn in self.tag_buttons:
            if btn.tag in selected_tags:
                btn.selected = True
                btn.configure(fg_color="#4CAF50", hover_color="#45a049")
    
    def toggle_tag(self, tag):
        for btn in self.tag_buttons:
            if btn.tag == tag:
                btn.selected = not btn.selected
                if btn.selected:
                    btn.configure(fg_color="#4CAF50", hover_color="#45a049")
                else:
                    btn.configure(fg_color=("gray75", "gray25"), hover_color=("gray70", "gray30"))
                break
        self.update_selection()
    
    def select_all_tags(self):
        for btn in self.tag_buttons:
            btn.selected = True
            btn.configure(fg_color="#4CAF50", hover_color="#45a049")
        self.update_selection()
    
    def clear_all_tags(self):
        for btn in self.tag_buttons:
            btn.selected = False
            btn.configure(fg_color=("gray75", "gray25"), hover_color=("gray70", "gray30"))
        self.update_selection()
    
    def filter_tags(self):
        """Filter tags based on search term"""
        search_term = self.tag_search_var.get().lower().strip()
        
        # Clear the grid first
        for widget in self.tag_grid_frame.winfo_children():
            widget.destroy()
        
        # Recreate the grid with filtered tags
        self.tag_buttons = []
        
        if search_term:
            filtered_tags = [tag for tag in self.available_tags if search_term in tag.lower()]
        else:
            filtered_tags = self.available_tags
        
        # Calculate number of columns
        button_width = 120
        padding = 10
        available_width = 350
        cols = max(1, available_width // (button_width + padding))
        
        row = 0
        col = 0
        
        for tag in filtered_tags:
            btn = ctk.CTkButton(
                self.tag_grid_frame,
                text=tag,
                command=lambda t=tag: self.toggle_tag(t),
                width=button_width,
                height=30
            )
            btn.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
            btn.tag = tag
            btn.selected = False
            self.tag_buttons.append(btn)
            
            col += 1
            if col >= cols:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(cols):
            self.tag_grid_frame.grid_columnconfigure(i, weight=1)
        
        # Restore selection state
        self.initialize_selected_tags()
    
    def clear_tag_search(self):
        """Clear tag search filter"""
        self.tag_search_var.set("")
        self.filter_tags()
    
    def update_selection(self):
        selected_tags = [btn.tag for btn in self.tag_buttons if btn.selected]
        self.current_var.set(", ".join(selected_tags))
    
    def preview_selection(self):
        """Preview the current tag selection without applying"""
        selected_tags = [btn.tag for btn in self.tag_buttons if btn.selected]
        if selected_tags:
            preview_text = f"Selected tags: {', '.join(selected_tags)}\n\nThis will filter tasks that have any of these tags."
        else:
            preview_text = "No tags selected.\n\nThis will show all tasks (no tag filtering)."
        
        messagebox.showinfo("Tag Selection Preview", preview_text)
    
    def apply_tags(self):
        self.result = self.current_var.get()
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()


if __name__ == "__main__":
    app = TaskManagerApp()
    app.run()
