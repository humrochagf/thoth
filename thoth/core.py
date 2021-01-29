import re
from subprocess import call
from typing import Iterator, Optional

import arrow
import toml
import yaml
from rich.console import Console
from sqlalchemy import String, cast, or_
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from .config import settings
from .data import Log, PydanticLog, build_db

LOG_YAML = (
    "---\n"
    "channel: {log.channel}\n"
    "tags: {log.tags}\n"
    "title: {log.title}\n"
    "---\n"
    "{log.body}"
)
LOG_TOML = (
    "+++\n"
    'channel = "{log.channel}"\n'
    "tags = {log.tags}\n"
    'title = "{log.title}"\n'
    "+++\n"
    "{log.body}"
)
LOG_YAML_RE = re.compile(
    r"^---\n(?P<meta>[\s\S]*)---\n(?P<body>[\s\S]*)$", re.MULTILINE
)
LOG_TOML_RE = re.compile(
    r"^\+\+\+\n(?P<meta>[\s\S]*)\+\+\+\n(?P<body>[\s\S]*)$", re.MULTILINE
)

console = Console()


class Thoth:
    def __init__(self):
        self.root_path = settings.root_path
        self.root_path.mkdir(parents=True, exist_ok=True)

        self.tmp_file = self.root_path / "tmp.md"

        self.db = build_db()

    def log(self, log: PydanticLog) -> PydanticLog:
        with self.tmp_file.open("w+", encoding="utf8") as fp:
            if settings.front_matter_format == "toml":
                fp.write(LOG_TOML.format(log=log))
            else:
                fp.write(LOG_YAML.format(log=log))

            fp.flush()
            call([settings.editor, fp.name])
            fp.seek(0)

            meta = {}
            content = fp.read()

            if match := LOG_YAML_RE.search(content):
                meta = yaml.safe_load(match.groupdict()["meta"])
                body = match.groupdict()["body"]

            elif match := LOG_TOML_RE.search(content):
                meta = toml.loads(match.groupdict()["meta"])
                body = match.groupdict()["body"]

            log.channel = meta["channel"]
            log.tags = meta["tags"]
            log.title = meta["title"]
            log.end = log.end or arrow.utcnow()
            log.body = body.strip()

        self.tmp_file.unlink()

        if log.channel not in settings.channels:
            console.print("Aborting log due to invalid channel.")

            return None

        if log.title:
            if log.id:
                self.db.query(Log).filter(Log.id == log.id).update(log.dict())
                self.db.commit()

                return log
            else:
                log_entry = Log(**log.dict())

                self.db.add(log_entry)
                self.db.commit()

                return PydanticLog.from_orm(log_entry)
        else:
            console.print("Aborting log due to empty log message.")

            return None

    def query_logs(
        self,
        query_string: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> Iterator[PydanticLog]:
        query = self.db.query(Log)

        if query_string is not None:
            query = query.filter(or_(
                Log.title.ilike(f"%{query_string}%"),
                Log.body.ilike(f"%{query_string}%"),
                Log.tags.ilike([f"%{query_string}%"]),
            ))
        elif channel is not None:
            query = query.filter(Log.channel == channel)
        else:
            query = query.all()

        for item in query:
            yield PydanticLog.from_orm(item)

    def get_log(self, id: str) -> PydanticLog:
        try:
            return PydanticLog.from_orm(
                self.db.query(Log)
                .filter(cast(Log.id, String).startswith(id))
                .one()
            )
        except MultipleResultsFound:
            return None
        except NoResultFound:
            return None

    def delete_log(self, log: PydanticLog):
        self.db.query(Log).filter(Log.id == log.id).delete()
        self.db.commit()
