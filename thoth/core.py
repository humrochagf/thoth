import json
from typing import Iterator

from tinydb import TinyDB

from .config import settings
from .data import Log

LOG_TEMPLATE = "---\ntags: {tags}\n---\n{message}"


class Thoth:
    def __init__(self):
        self.root_path = settings.root_path
        self.root_path.mkdir(parents=True, exist_ok=True)

        self.log_path = settings.log_path
        self.log_path.mkdir(parents=True, exist_ok=True)

        self.db = TinyDB(settings.database_file)

    def log(self, message: str, channel: str) -> Log:
        channel = channel or settings.default_channel
        path = self.log_path / channel
        path.mkdir(parents=True, exist_ok=True)

        log = Log(channel=channel, message=message)
        self.db.insert(json.loads(log.json()))

        with open(path / log.filename, "x") as fp:
            fp.write(LOG_TEMPLATE.format(**log.dict()))

        return log

    def query_logs(self) -> Iterator[Log]:
        for item in self.db.all():
            yield Log(**item)
