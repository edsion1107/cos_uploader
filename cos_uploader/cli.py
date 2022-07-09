import time
from pathlib import Path

import typer
from loguru import logger
from watchdog.observers import Observer

from cos_uploader.handler import MyEventHandler

app = typer.Typer(no_args_is_help=True,add_completion=False)


@app.command()
def main(
        path: Path = typer.Argument(
            ...,
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
            resolve_path=True
        ),
        secret_id: str = typer.Option(..., envvar="COS_SECRET_ID"),
        secret_key: str = typer.Option(..., envvar="COS_SECRET_KEY"),
        region: str = typer.Option(..., envvar="COS_REGION"),
        bucket: str = typer.Option(..., envvar="COS_BUCKET"),
):
    typer.echo("start watching")
    event_handler = MyEventHandler(path, secret_id, secret_key, region, bucket)
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        typer.echo("stop watching")
        observer.stop()

if __name__ == '__main__':
    app()