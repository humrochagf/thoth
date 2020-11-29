from typing import Optional

import typer
from dynaconf.loaders import toml_loader

from .config import settings
from .core import Thoth

app = typer.Typer()
thoth = Thoth()


@app.command()
def log(
    message: str = typer.Option("", "--message", "-m"),
    channel: str = typer.Option(None, "--channel", "-c"),
):
    if channel is not None and channel not in settings.channels:
        typer.echo(f"Invalid channel. Pick one from {settings.channels}")
    else:
        log = thoth.log(message, channel)

        typer.echo(
            f"[{log.created_at:%Y-%m-%d %H:%M}]({log.channel}) {log.message}"
        )


@app.command()
def ls():
    for log in thoth.query_logs():
        typer.echo(
            f"[{log.created_at:%Y-%m-%d %H:%M}]({log.channel}) {log.message}"
        )


@app.command()
def config(key: str, value: Optional[str] = None):
    key = key.lower()

    if not settings.exists(key):
        typer.echo(f"The key {key} is invalid.")
    elif value is None:
        typer.echo(settings.get(key))
    else:
        if key == "default_channel" and value not in settings.channels:
            typer.echo(f"Invalid channel. Pick one from {settings.channels}")
        else:
            toml_loader.write(settings.config_file, {key: value}, merge=True)
