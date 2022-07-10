import os
from importlib.resources import as_file, files
from pathlib import Path

from loguru import logger
from qcloud_cos import CosClientError, CosConfig, CosS3Client, CosServiceError
from watchdog.events import FileSystemEventHandler

import cos_uploader


class MyEventHandler(FileSystemEventHandler):
    client: CosS3Client
    bucket: str
    base_path: Path

    def __init__(
        self, base_path: Path, secret_id: str, secret_key: str, region: str, bucket: str
    ):
        config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
        self.client = CosS3Client(config)
        assert Path(base_path).is_dir()
        self.base_path = base_path
        if not self.client.bucket_exists(bucket):
            raise CosClientError
        else:
            self.bucket = bucket
        # self.create_empty_file()

    @DeprecationWarning
    def _create_empty_file(self):
        """创建空文件用于创建文件夹——对象存储不支持文件夹"""
        if self._empty_file.is_file():
            if not self._empty_file.stat().st_size == 0:
                logger.warning("empty file size is not '0'")
                self._empty_file.unlink()
            else:
                return
        self._empty_file.write_bytes(b"")
        self._empty_file.chmod(0o444)

    def _remote_filename(self, local: os.PathLike, is_dir: bool):
        remote = Path(local).relative_to(self.base_path).as_posix()
        if is_dir:
            remote += "/"
        return remote

    def _empty_file(self):
        with as_file(files(cos_uploader).joinpath("empty")) as f:
            return f.resolve()

    def on_any_event(self, event):
        logger.info(f"{event=}")

    # 文件移动
    def on_moved(self, event):
        print(event)

    def on_created(self, event):
        try:
            if event.is_directory:
                res = self.client.upload_file(
                    Bucket=self.bucket,
                    Key=self._remote_filename(event.src_path, True),
                    LocalFilePath=self._empty_file(),
                )
            else:
                res = self.client.upload_file(
                    Bucket=self.bucket,
                    Key=self._remote_filename(event.src_path, False),
                    LocalFilePath=event.src_path,
                    EnableMD5=True,
                )
            logger.info(f"{res=}")
        except (CosClientError, CosServiceError):
            logger.exception("upload failed")

    def on_deleted(self, event):
        local_file = Path(event.src_path)
        remote = self._remote_filename(local_file, event.is_directory)
        try:
            res = self.client.delete_object(Bucket=self.bucket, Key=remote)
            logger.info(f"{res=}")
        except (CosClientError, CosServiceError):
            logger.exception("upload failed")

    def on_modified(self, event):
        print(event)
