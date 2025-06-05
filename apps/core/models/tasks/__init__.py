# apps/follow_up/models/__init__.py
from .task import Task
from .task_history import TaskHistory
from .task_type import TaskType
from .task_status import TaskStatus
from .task_origin import TaskOrigin
from .user_task import UserTask

__all__ = [
    'Task',
    'TaskHistory',
    'TaskType',
    'TaskStatus',
    'TaskOrigin',
    'System',
    'UserTask'
]