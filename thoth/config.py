from pathlib import Path

from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="THOTH",
)

settings.editor = "vim"

settings.front_matter_format = "yaml"

settings.root_path = Path.home() / ".thoth"

settings.config_file = settings.root_path / "config.toml"

settings.database_file = settings.root_path / "thoth.db"

settings.database_url = f"sqlite:///{settings.database_file}"

settings.channels = ["work", "life", "health", "hobby", "tip"]

settings.default_channel = settings.channels[0]

settings.load_file(settings.config_file.as_posix())
