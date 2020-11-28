import typer

from .core import Thoth

app = typer.Typer()
thoth = Thoth()


@app.command()
def log(message: str):
    log = thoth.log(message)

    typer.echo(f"[{log.created_at:%Y-%m-%d %H:%M}] {log.message}")


@app.command()
def ls():
    for log in thoth.query_logs():
        typer.echo(f"[{log.created_at:%Y-%m-%d %H:%M}] {log.message}")
