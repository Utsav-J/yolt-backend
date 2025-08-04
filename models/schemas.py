from typing     import Optional
from pydantic   import BaseModel, Field

class TextInput(BaseModel):
    text: str


class Task(BaseModel):
    id: Optional[str] = Field(None, description="Optional task ID, e.g., UUID")
    title: str = Field(..., description="Short description or name of the task")
    description: Optional[str] = Field(None, description="Additional context or notes")
    priority: Optional[int] = Field(None, ge=1, le=5, description="1 (low) to 5 (high) priority scale")

class Tasks(BaseModel):
    tasks: list[Task]