from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

import pendulum
from pydantic import BaseModel


class Log(BaseModel):

    id: UUID = uuid4()
    channel: str
    tags: List[str] = []
    message: str
    start: datetime = pendulum.now()
    end: Optional[datetime] = None

    @property
    def filename(self):
        return f"{self.id.hex}.md"
