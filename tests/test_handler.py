import logging
import os
import uuid
from pathlib import Path

import pytest
from cos_uploader.handler import MyEventHandler
from watchdog.events import FileCreatedEvent, FileDeletedEvent,DirCreatedEvent


@pytest.fixture()
def handler(tmp_path):
    secret_id = os.getenv("COS_SECRET_ID")
    secret_key = os.getenv("COS_SECRET_KEY")
    region = os.getenv("COS_REGION")
    bucket = os.getenv("COS_BUCKET")
    assert secret_id
    hdlr = MyEventHandler(tmp_path, secret_id, secret_key, region, bucket)
    return hdlr


@pytest.fixture(params=["is_dir", "is_file"])
def local(tmp_path: Path, request):
    local = tmp_path.joinpath(str(uuid.uuid4()))
    if request.param == "is_file":
        local.touch()
        yield local
        if local.exists():
            local.unlink()
    else:
        local.mkdir()
        yield local
        if local.exists():
            local.rmdir()


def test_on_create_event(local:Path, handler: MyEventHandler):
    if local.is_file():
        event = FileCreatedEvent(local)
    else:
        event = DirCreatedEvent(local)
    logging.info(event)
    handler.on_created(event)


def test_on_delete_event(local_file_and_folder, handler: MyEventHandler):
    event = FileDeletedEvent(local_file_and_folder)
    handler.on_deleted(event)
