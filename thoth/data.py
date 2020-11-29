from datetime import datetime
from typing import List, Optional

import pendulum
from pydantic import BaseModel


class Log(BaseModel):

    channel: str
    tags: List[str] = []
    message: str
    created_at: datetime = pendulum.now()
    stopped_at: Optional[datetime] = None

    @property
    def filename(self):
        return f"{self.created_at:%Y%m%d%H%M%S}.md"
