from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel

from thoth.config import settings


class Log(BaseModel):

    id: UUID = uuid4()

    title: str
    body: str = ""

    channel: str = settings.default_channel
    tags: list[str] = []

    start: datetime = datetime.now(timezone.utc)
    end: Optional[datetime] = None

    time_spent: timedelta = timedelta()
