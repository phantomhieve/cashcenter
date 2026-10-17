import enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TaskType(enum.Enum):
    FAST = "fast"          # gemini-3.8-flash for high-speed preprocessing & validation
    REASONING = "reasoning" # gemini-4-argon for deep synthesis & reflective feedback


class AIResponse(BaseModel):
    text: str
    model: str
    task_type: str
    tokens_used: Optional[int] = None
    structured_data: Optional[Dict[str, Any]] = None
    latency_ms: Optional[float] = None
