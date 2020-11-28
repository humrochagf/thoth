from datetime import datetime
from typing import List, Optional

import pendulum
from pydantic import BaseModel


class Channel(BaseModel):

    key: str
    name: str
    color: str


class Log(BaseModel):

    channel: str
    tags: List[str] = []
    message: str
    created_at: datetime = pendulum.now()
    stopped_at: Optional[datetime] = None
