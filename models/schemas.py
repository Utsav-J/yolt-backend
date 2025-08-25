from typing     import Optional
from pydantic   import BaseModel, Field
from enum import Enum

class TextInput(BaseModel):
    text: str

class PriorityLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class Task(BaseModel):
    title: str = Field(..., description="Short description or name of the task")
    description: Optional[str] = Field(None, description="Additional context or notes")
    priority: Optional[PriorityLevel] = Field(None, description="Priority level: high, medium, or low")

class Tasks(BaseModel):
    tasks: list[Task]

    
class DailyAffirmation(BaseModel):
    affirmationText: str