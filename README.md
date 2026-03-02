# Desktop Task Manager

A modern, user-friendly desktop task management application built with Python and CustomTkinter.

## Features

- ✅ **Modern GUI Interface** - Clean, intuitive desktop application
- ➕ **Add Tasks** - Create tasks with title, description, due date, and tags
- 📝 **List & View Tasks** - Professional table display with all task details
- ✏️ **Edit Tasks** - Update any task field with validation
- ✅ **Complete Tasks** - Mark tasks as completed with one click
- 🗑️ **Delete Tasks** - Remove tasks with confirmation
- 🔍 **Smart Search** - Intelligent search with partial matching and typo tolerance
- 📋 **Tag Selector** - Visual tag selection with grid layout and search
- 📊 **Flexible Sorting** - Sort by title, due date, creation date, or status
- ⌨️ **Keyboard Shortcuts** - Quick actions for power users
- 💾 **JSON Storage** - All data saved to local JSON file
- 🎨 **Modern Design** - Beautiful, responsive interface
- 📅 **Date Picker** - User-friendly calendar widget for due dates
- 🔔 **Smart Notifications** - Automatic reminders for due and overdue tasks
- ⏰ **Due Task Alerts** - Quick view of tasks due in the next 24 hours

## Screenshots

The application features:
- Clean, modern interface with professional styling
- Comprehensive task list with all details visible
- Easy-to-use filtering and sorting controls
- Intuitive add/edit dialogs with validation
- Keyboard shortcuts for quick actions
- Status bar with helpful information

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone or download the project:**
   ```bash
   git clone https://github.com/yato-sketch/task-management-desktop.git
   cd desktop-task-manage-app
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   # Option 1: Use the launcher script (recommended)
   ./run.sh
   
   # Option 2: Manual setup
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 main.py
   ```

4. **Optional - Load demo data:**
   ```bash
   source venv/bin/activate
   python3 demo.py
   ```

## Usage

### Basic Operations

1. **Adding a Task:**
   - Click the "➕ Add Task" button or press `Ctrl+N`
   - Fill in the task details in the dialog
   - Click "Save" to create the task

2. **Viewing Tasks:**
   - All tasks are displayed in the main table
   - Use filters to narrow down the list
   - Click on any task row to select it

3. **Editing a Task:**
   - Select a task by clicking on it
   - Click "✏️ Edit" button or press `Enter`
   - Modify the task details in the dialog
   - Click "Save" to update

4. **Completing a Task:**
   - Select a task by clicking on it
   - Click "✅ Complete" button
   - The task status will change to completed

5. **Deleting a Task:**
   - Select a task by clicking on it
   - Click "🗑️ Delete" button or press `Delete`
   - Confirm the deletion in the dialog

6. **Checking Due Tasks:**
   - Click "⏰ Due Tasks" button to see tasks due in the next 24 hours
   - View overdue tasks and tasks due soon
   - Get a quick overview of urgent tasks

### Smart Search & Filtering

- **Intelligent Search:** 
  - Partial matching: "doc" finds "documentation"
  - Multiple words: "meeting team" finds tasks with both words
  - Typo tolerance: "meating" finds "meeting"
  - Case insensitive: Works with any capitalization
- **Status Filter:** Choose "all", "pending", or "completed"
- **Tags Filter:** 
  - Click the 📋 button to open visual tag selector
  - Select from all existing tags in a grid layout
  - Search tags by typing in the search box
  - Use "Select All" or "Clear All" for bulk operations
  - Click "Preview" to see selection before applying
  - Click "Apply & Find" to apply the tag filter
  - Click 🔍 Find to apply filters (main window)
  - Click 🗑️ Clear to reset all filters
- **Sort By:** Choose field to sort by (created_at, title, due_date, status)
- **Sort Direction:** Choose ascending or descending order
- **Search Help:** Click the "?" button for search tips and examples

### Keyboard Shortcuts

- `Ctrl+N` - Add new task
- `F5` - Refresh task list
- `Delete` - Delete selected task
- `Enter` - Edit selected task
- `Ctrl+F` - Apply filters (Find)
- `Escape` - Clear all filters

**Tag Selector Modal:**
- `Enter` - Apply & Find selected tags
- `Escape` - Cancel tag selection
- `Ctrl+P` - Preview current selection

## Data Storage

Tasks are automatically saved to a `tasks.json` file in the application directory. The file is created automatically when you add your first task.

### Data Format

```json
[
  {
    "id": "abc123def456",
    "title": "Task title",
    "description": "Optional description",
    "due_date": "2025-12-31T00:00:00",
    "tags": ["tag1", "tag2"],
    "status": "pending",
    "created_at": "2025-01-01T00:00:00",
    "updated_at": "2025-01-01T00:00:00"
  }
]
```

## Project Structure

```
desktop-task-manage-app/
├── main.py              # Main application and GUI
├── models.py            # Data models and types
├── task_service.py      # Business logic and operations
├── storage.py           # Data persistence layer
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── tasks.json          # Task data (created automatically)
```

## Technical Details

### Dependencies

- **customtkinter** - Modern, customizable tkinter widgets
- **Pillow** - Image processing (required by customtkinter)
- **tkcalendar** - Date picker widget for better date input
- **plyer** - Cross-platform notifications

### Architecture

- **Models** - Data structures and validation
- **Storage** - JSON file persistence with repository pattern
- **Service** - Business logic and operations
- **GUI** - Modern desktop interface with CustomTkinter

### Key Features

- **Modern GUI Interface** - Clean, intuitive desktop application
- **Complete Task Management** - Add, edit, complete, delete tasks
- **Advanced Filtering & Sorting** - Filter by status, tags, search terms
- **Professional Display** - Clean table with proper alignment
- **Keyboard Shortcuts** - Power user features
- **JSON Data Storage** - Reliable local data persistence
- **Error Handling** - Comprehensive validation and user-friendly messages

## Notification System

The application includes a smart notification system that runs in the background:

### Automatic Notifications
- **Due Soon**: Notifications appear 1 hour before a task is due
- **Overdue**: Immediate notifications for tasks that are past their due date
- **Background Monitoring**: Checks for due tasks every minute
- **Cross-Platform**: Works on Windows, macOS, and Linux

### Notification Features
- **Visual Alerts**: System notifications with task details
- **Time Information**: Shows how much time is remaining or overdue
- **Smart Filtering**: Only notifies once per task to avoid spam
- **Auto-Clear**: Notifications are cleared when tasks are completed

### Testing Features

**Test Notifications:**
```bash
source venv/bin/activate
python3 test_notifications.py
```

**Test Search Functionality:**
```bash
source venv/bin/activate
python3 test_search.py
```

## Error Handling

The application includes comprehensive error handling:
- Input validation with clear error messages
- File operation error handling
- User-friendly error dialogs
- Graceful handling of missing data

## Future Enhancements

Potential improvements for future versions:
- Dark/light theme toggle
- Task categories and projects
- Due date reminders and notifications
- Task export/import functionality
- Data backup and restore
- Task templates
- Progress tracking and statistics

## Troubleshooting

### Common Issues

1. **Application won't start:**
   - Ensure Python 3.8+ is installed
   - Install dependencies: `pip install -r requirements.txt`

2. **Tasks not saving:**
   - Check file permissions in the application directory
   - Ensure the directory is writable

3. **GUI looks different:**
   - CustomTkinter may render differently on different systems
   - Try different appearance modes in the code

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions, please create an issue in the repository.
