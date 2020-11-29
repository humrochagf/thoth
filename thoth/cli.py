from typing import Optional

import typer
from dynaconf.loaders import toml_loader

from . import __version__
from .config import settings
from .core import Thoth
from .data import Log

app = typer.Typer()
thoth = Thoth()


def echo_log(log: Log):
    channel = typer.style(log.channel, fg=typer.colors.BLUE)
    created_at = typer.style(
        f"({log.created_at:%Y-%m-%d %H:%M})", fg=typer.colors.GREEN
    )
    typer.echo(f"* {channel} - {created_at} {log.message}")


@app.command()
def version():
    """
    Show thoth version.
    """
    typer.echo(__version__)


@app.command()
def log(
    message: str = typer.Option("", "--message", "-m"),
    channel: str = typer.Option("", "--channel", "-c"),
):
    """
    Log a new activity.
    """
    channel = channel or settings.default_channel

    if channel not in settings.channels:
        typer.echo(f"Invalid channel. Pick one from {settings.channels}")
    else:
        log = Log(channel=channel, message=message)

        if thoth.log(log):
            echo_log(log)


@app.command()
def list():
    """
    List logged activities.
    """
    for log in thoth.query_logs():
        echo_log(log)


@app.command()
def config(key: str, value: Optional[str] = None):
    """
    Manage thoth configuration options.
    """
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
