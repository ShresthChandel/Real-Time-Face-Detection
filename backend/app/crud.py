from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models, schemas

async def create_roi_event(db: AsyncSession, roi: schemas.RoiEventCreate):
    db_roi = models.RoiEvent(
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

async def get_roi_events(db: AsyncSession, limit: int = 50):
    query = select(models.RoiEvent).order_by(models.RoiEvent.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
