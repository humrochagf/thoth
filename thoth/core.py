import json
from typing import Iterator

from tinydb import TinyDB

from . import settings
from .data import Channel, Log


class Thoth():

    def __init__(self):
        self.root_path = settings.ROOT_PATH
        self.root_path.mkdir(parents=True, exist_ok=True)

        self.db = TinyDB(self.root_path / settings.DATABASE_NAME)

        channel_key = "work"
        channel_data = settings.CHANNELS[channel_key]
        self.channel = Channel(key=channel_key, **channel_data)

    def log(self, message: str) -> Log:
        log = Log(channel=self.channel.key, message=message)

        self.db.insert(json.loads(log.json()))

        return log

    def query_logs(self) -> Iterator[Log]:
        for item in self.db.all():
            yield Log(**item)
