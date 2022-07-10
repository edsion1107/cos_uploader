import os
import uuid
from pathlib import Path

import pytest
from cos_uploader.handler import MyEventHandler
from watchdog.events import FileCreatedEvent


@pytest.fixture()
def handler(tmp_path):
    hdlr = MyEventHandler(
        tmp_path,
        secret_id=os.getenv("COS_SECRET_ID"),
        secret_key=os.getenv("COS_SECRET_KEY"),
        region=os.getenv("COS_REGION"),
        bucket=os.getenv("COS_BUCKET"),
    )
    return hdlr


@pytest.fixture(params=[True, False])
def local_file_and_folder(tmp_path: Path, request):
    local = tmp_path.joinpath(str(uuid.uuid4()))
    if request.param:
        local.touch()
        yield local
        local.unlink()
    else:
        local.mkdir()
        yield local
        local.rmdir()


def test_on_create_event(local_file_and_folder, handler: MyEventHandler):
    event = FileCreatedEvent(local_file_and_folder)
    handler.on_created(event)
