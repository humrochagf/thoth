from typing import Optional

import arrow
import typer
from dynaconf.loaders import toml_loader
from rich.console import Console
from rich.markdown import Markdown

from thoth import __version__
from thoth.config import settings
from thoth.core import Thoth
from thoth.data import Log
from thoth.exceptions import ThothException

app = typer.Typer()
thoth = Thoth()
console = Console(highlight=False)


def echo_log(log: Log, verbose: bool = False) -> None:
    log_id = f"[blue]{log.id.hex[:7]}[/blue]"
    channel = f"[yellow]{log.channel}[/yellow]"
    status = "[green]done[/green]" if log.end else "[yellow]pending[/yellow]"
    start = f"[green]({arrow.get(log.start).humanize()})[/green]"

    message: str | Markdown

    if verbose:
        message = Markdown(f"\n# {log.title}\n\n{log.body}", hyperlinks=False)
    else:
        message = log.title

    console.print(f"* {log_id} - {channel} - {status} - {start}", message)


@app.command()
def version() -> None:
    """
    Show thoth version.
    """
    console.print(__version__)


@app.command()
def log(
    message: str = typer.Option("", "--message", "-m"),
    channel: str = typer.Option("", "--channel", "-c"),
    start: str = typer.Option(None, "--start", "-s"),
    end: str = typer.Option(None, "--end", "-e"),
) -> None:
    """
    Log a new activity.
    """
    channel = channel or settings.default_channel

    if channel not in settings.channels:
        console.print(f"Invalid channel. Pick one from {settings.channels}")

        raise typer.Abort()

    message_lines = message.strip().splitlines() or [""]
    title = message_lines[0]
    body = "\n".join(message_lines[1:])

    log = Log(channel=channel, title=title, body=body)

    if start:
        try:
            log.start = arrow.get(start).datetime
        except arrow.ParserError:
            console.print("Invalid start datetime format.")

            raise typer.Abort()

    if end:
        try:
            log.end = arrow.get(end).datetime
        except arrow.ParserError:
            console.print("Invalid end datetime format.")

            raise typer.Abort()

    try:
        log = thoth.log(log)
    except ThothException as e:
        console.print(e)

        raise typer.Abort()

    echo_log(log)


@app.command()
def show(id: str) -> None:
    """
    Show a specific log.
    """
    if log := thoth.get_log(id):
        echo_log(log, True)


@app.command()
def list(
    channel: Optional[str] = typer.Option(None, "--channel", "-c"),
) -> None:
    """
    List logged activities.
    """
    for log in thoth.query_logs(channel=channel):
        echo_log(log)


@app.command()
def search(query: str) -> None:
    """
    Search into the log content, tag or title given a query.
    """
    for log in thoth.query_logs(query_string=query):
        echo_log(log)


@app.command()
def edit(id: str) -> None:
    """
    Edit a specific log.
    """
    if log := thoth.get_log(id):
        if log := thoth.log(log):
            echo_log(log)
        else:
            raise typer.Abort()


@app.command()
def delete(id: str) -> None:
    """
    Delete a specific log.
    """
    if log := thoth.get_log(id):
        thoth.delete_log(log)


@app.command()
def config(key: str, value: Optional[str] = None) -> None:
    """
    Manage thoth configuration options.
    """
    key = key.lower()

    if not settings.exists(key):
        console.print(f"The key {key} is invalid.")
    elif value is None:
        console.print(settings.get(key))
    else:
        if key == "default_channel" and value not in settings.channels:
            console.print(
                f"Invalid channel. Pick one from {settings.channels}"
            )
        else:
            toml_loader.write(settings.config_file, {key: value}, merge=True)
