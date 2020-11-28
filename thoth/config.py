from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="THOTH",
)

settings.root_path = Path.home() / ".thoth"

settings.config_file = settings.root_path / "config.toml"

settings.database_file = settings.root_path / "db.json"

settings.channels = ["work", "life", "health", "hobby"]

settings.default_channel = settings.channels[0]

settings.load_file(settings.config_file.as_posix())
