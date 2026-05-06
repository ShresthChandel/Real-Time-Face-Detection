import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schemas

logger = logging.getLogger(__name__)

async def create_roi_event(db: AsyncSession, roi: schemas.RoiEventCreate):
    logger.info(f"Creating ROI event for session {roi.session_id}, frame {roi.frame_id}")
    db_roi = models.RoiEvent(
        session_id=roi.session_id,
        frame_id=roi.frame_id,
        x=roi.x,
        y=roi.y,
        w=roi.w,
        h=roi.h,
        confidence=roi.confidence
    )
    db.add(db_roi)
    await db.commit()
    await db.refresh(db_roi)
    return db_roi

async def get_roi_events(db: AsyncSession, limit: int = 50, offset: int = 0):
    query = select(models.RoiEvent).order_by(models.RoiEvent.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
