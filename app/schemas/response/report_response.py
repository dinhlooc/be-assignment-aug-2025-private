from pydantic import BaseModel
from typing import Dict, List, Any

class TaskCountByStatusResponse(BaseModel):
    project_id: str
    status_counts: Dict[str, int]  # {"todo": 5, "in_progress": 3, "completed": 10}

class OverdueTasksResponse(BaseModel):
    project_id: str
    overdue_tasks: List[Dict[str, Any]]
    total_overdue: int