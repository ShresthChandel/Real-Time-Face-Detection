from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class RoiEventBase(BaseModel):
    frame_id: int
    x: int
    y: int
    w: int
    h: int
    confidence: float | None = None

class RoiEventCreate(RoiEventBase):
    pass

class RoiEvent(RoiEventBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
