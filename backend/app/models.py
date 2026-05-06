import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class RoiEvent(Base):
    __tablename__ = "roi_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    frame_id = Column(BigInteger, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    w = Column(Integer, nullable=False)
    h = Column(Integer, nullable=False)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
