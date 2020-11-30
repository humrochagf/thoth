import json
import re
from subprocess import call
from typing import Iterator

import pendulum
import toml
import typer
import yaml
from tinydb import TinyDB, where

from .config import settings
from .data import Log

LOG_YAML = "---\nchannel: {channel}\ntags: {tags}\n---\n{message}"
LOG_TOML = '+++\nchannel = "{channel}"\ntags = {tags}\n+++\n{message}'
LOG_YAML_RE = re.compile(
    r"^---\n(?P<meta>[\s\S]*)---\n(?P<body>[\s\S]*)$", re.MULTILINE
)
LOG_TOML_RE = re.compile(
    r"^\+\+\+\n(?P<meta>[\s\S]*)\+\+\+\n(?P<body>[\s\S]*)$", re.MULTILINE
)


class Thoth:
    def __init__(self):
        self.root_path = settings.root_path
        self.root_path.mkdir(parents=True, exist_ok=True)

        self.log_path = settings.log_path
        self.log_path.mkdir(parents=True, exist_ok=True)

        self.db = TinyDB(settings.database_file)

    def log(self, log: Log) -> bool:
        with open(self.log_path / log.filename, "x+") as fp:
            if settings.front_matter_format == "toml":
                fp.write(LOG_TOML.format(**log.dict()))
            else:
                fp.write(LOG_YAML.format(**log.dict()))

            if not log.message:
                fp.flush()
                call([settings.editor, fp.name])
                fp.seek(0)

                meta = {}
                content = fp.read()

                if match := LOG_YAML_RE.search(content):
                    meta = yaml.safe_load(match.groupdict()["meta"])
                    content = match.groupdict()["body"]
                elif match := LOG_TOML_RE.search(content):
                    meta = toml.loads(match.groupdict()["meta"])
                    content = match.groupdict()["body"]

                content = content.strip()

                if content:
                    log.message = content.splitlines()[0].strip()

                log.channel = meta["channel"]
                log.tags = meta["tags"]
                log.stopped_at = pendulum.now()

                fp.seek(0)
                fp.truncate()
                fp.write(content)

        if log.channel not in settings.channels:
            typer.echo("Aborting log due to invalid channel.")
            (self.log_path / log.filename).unlink()

            return False

        if log.message:
            self.db.insert(json.loads(log.json()))

            return True
        else:
            typer.echo("Aborting log due to empty log message.")
            (self.log_path / log.filename).unlink()

            return False

    def query_logs(self, channel: str = "") -> Iterator[Log]:
        if channel:
            query = self.db.search(where("channel") == channel)
        else:
            query = self.db.all()

        for item in query:
            yield Log(**item)
