from typing import List, Optional
from uuid import UUID, uuid4

import arrow
from arrow import Arrow
from pydantic_sqlalchemy import sqlalchemy_to_pydantic
from sqlalchemy import Column, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import ArrowType, ScalarListType, UUIDType

from .config import settings

Base = declarative_base()

engine = create_engine(settings.database_url)


class Log(Base):

    __tablename__ = "logs"

    id = Column(
        UUIDType(version=4, binary=False),
        primary_key=True,
        index=True,
        default=uuid4,
    )

    channel = Column(String, default=settings.default_channel)
    tags = Column(ScalarListType, default=list)
    title = Column(String, default=str)
    body = Column(Text, default=str)
    start = Column(ArrowType, default=arrow.utcnow)
    end = Column(ArrowType)

    def __repr__(self):
        return f"<Log(channel='{self.channel}', title='{self.title}')>"


PydanticLogBase = sqlalchemy_to_pydantic(Log)


class PydanticLog(PydanticLogBase):

    id: Optional[UUID]
    channel: str = settings.default_channel
    tags: List[str] = []
    title: str = ""
    body: str = ""
    start: Arrow = arrow.utcnow()
    end: Optional[Arrow]

    class Config:
        arbitrary_types_allowed = True


def build_db() -> Session:
    Base.metadata.create_all(engine)

    LocalSession = sessionmaker(bind=engine)

    return LocalSession()
