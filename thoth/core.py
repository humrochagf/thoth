import json
import re
from subprocess import call
from tempfile import NamedTemporaryFile
from typing import Iterator, Optional

import toml
import yaml
from tinydb import TinyDB, where

from thoth.config import DATABASE_FILE, settings
from thoth.data import Log
from thoth.exceptions import ThothException

LOG_YAML = "---\n{meta}---\n{body}"
LOG_YAML_RE = re.compile(
    r"^---\n(?P<meta>[\s\S]*)---\n(?P<body>[\s\S]*)$", re.MULTILINE
)

LOG_TOML = "+++\n{meta}+++\n{body}"
LOG_TOML_RE = re.compile(
    r"^\+\+\+\n(?P<meta>[\s\S]*)\+\+\+\n(?P<body>[\s\S]*)$", re.MULTILINE
)


class Thoth:

    db: TinyDB

    def __init__(self):
        DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

        self.db = TinyDB(
            DATABASE_FILE, sort_keys=True, indent=2, separators=(",", ": ")
        )

    def log(self, log: Log) -> Log:
        with NamedTemporaryFile("w+", encoding="utf8", suffix=".md") as fp:
            log_dict = json.loads(
                log.json(include={"title", "channel", "tags", "custom_data"})
            )

            if settings.front_matter_format == "toml":
                fp.write(
                    LOG_TOML.format(
                        meta=toml.dumps(log_dict),
                        body=log.body,
                    )
                )
            else:
                fp.write(
                    LOG_YAML.format(
                        meta=yaml.safe_dump(log_dict),
                        body=log.body,
                    )
                )

            fp.flush()
            call([settings.editor, fp.name])
            fp.seek(0)

            content = fp.read()

            if match := LOG_YAML_RE.search(content):
                meta = yaml.safe_load(match.groupdict()["meta"])
                body = match.groupdict()["body"]
            elif match := LOG_TOML_RE.search(content):
                meta = toml.loads(match.groupdict()["meta"])
                body = match.groupdict()["body"]
            else:
                meta = {}
                body = ""

            log.title = meta.get("title", log.title)
            log.channel = meta.get("channel", log.channel)
            log.tags = meta.get("tags", log.tags)
            log.custom_data = meta.get("custom_data", log.custom_data)
            log.body = body.strip()

        if log.channel not in settings.channels:
            raise ThothException("Invalid log channel.")

        if not log.title:
            raise ThothException("A log title is required.")

        self.db.upsert(json.loads(log.json()), where("id") == str(log.id))

        return log

    def query_logs(
        self,
        query_string: Optional[str] = None,
        channel: Optional[str] = None,
    ) -> Iterator[Log]:
        # TODO: text search
        if channel:
            query = self.db.search(where("channel") == channel)
        else:
            query = self.db.all()

        for item in query:
            yield Log(**item)

    def get_log(self, id: str) -> Optional[Log]:
        results = self.db.search(
            where("id").test(lambda value: value.startswith(id))  # type: ignore
        )

        if len(results) != 1:
            return None

        return Log(**results[0])

    def delete_log(self, log: Log) -> None:
        self.db.remove(where("id") == str(log.id))
