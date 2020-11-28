import json
from typing import Iterator

from tinydb import TinyDB

from .config import settings
from .data import Log


class Thoth():

    def __init__(self):
        self.root_path = settings.root_path
        self.root_path.mkdir(parents=True, exist_ok=True)

        self.db = TinyDB(settings.database_file)

    def log(self, message: str) -> Log:
        log = Log(channel=settings.default_channel, message=message)

        self.db.insert(json.loads(log.json()))

        return log

    def query_logs(self) -> Iterator[Log]:
        for item in self.db.all():
            yield Log(**item)
