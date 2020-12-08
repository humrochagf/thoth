from typing import Optional

import pendulum
import typer
from dynaconf.loaders import toml_loader
from pendulum.parsing import ParserError

from . import __version__
from .config import settings
from .core import Thoth
from .data import Log

app = typer.Typer()
thoth = Thoth()


def echo_log(log: Log, verbose: bool = False):
    log_id = typer.style(log.id.hex[:7], fg=typer.colors.BLUE)
    channel = typer.style(log.channel, fg=typer.colors.YELLOW)
    start = typer.style(f"({log.start:%Y %b %d %H:%M})", fg=typer.colors.GREEN)

    if verbose:
        with open(thoth.log_path / log.filename) as fp:
            content = fp.read()
            typer.echo(f"* {log_id} - {channel} - {start}\n{content}")
    else:
        typer.echo(f"* {log_id} - {channel} - {start} {log.message}")


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
    start: str = typer.Option(None, "--start", "-s"),
    end: str = typer.Option(None, "--end", "-e"),
):
    """
    Log a new activity.
    """
    channel = channel or settings.default_channel

    if channel not in settings.channels:
        typer.echo(f"Invalid channel. Pick one from {settings.channels}")
        raise typer.Abort()

    log = Log(channel=channel, message=message)

    if start:
        try:
            log.start = pendulum.parse(start)
        except ParserError:
            typer.echo("Invalid start datetime format.")
            raise typer.Abort()

    if end:
        try:
            log.end = pendulum.parse(end)
        except ParserError:
            typer.echo("Invalid start datetime format.")
            raise typer.Abort()

        if log.start > log.end:
            typer.echo("Log end must be greater than start.")
            raise typer.Abort()

    if thoth.log(log):
        echo_log(log)


@app.command()
def show(id: str):
    """
    Show a specific log.
    """
    if log := thoth.get_log(id):
        echo_log(log, True)


@app.command()
def list(channel: str = typer.Option("", "--channel", "-c")):
    """
    List logged activities.
    """
    for log in thoth.query_logs(channel):
        echo_log(log)


@app.command()
def edit(id: str):
    """
    Edit a specific log.
    """
    if log := thoth.get_log(id):
        thoth.edit_log(log)


@app.command()
def delete(id: str):
    """
    Delete a specific log.
    """
    if log := thoth.get_log(id):
        thoth.delete_log(log)


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
