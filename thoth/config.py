from pathlib import Path

from appdirs import AppDirs
from dynaconf import Dynaconf

dirs = AppDirs("thoth")

CONFIG_FILE = Path(dirs.user_config_dir) / "config.toml"
DATABASE_FILE = Path(dirs.user_data_dir) / "db.json"

settings = Dynaconf(envvar_prefix="THOTH")

settings.editor = "vim"

settings.front_matter_format = "yaml"

settings.channels = ["work", "personal"]

settings.default_channel = settings.channels[0]

settings.load_file(str(CONFIG_FILE))
