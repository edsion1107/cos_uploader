from pathlib import Path
from loguru import logger
from qcloud_cos import CosConfig, CosS3Client, CosClientError, CosServiceError
from importlib.resources import as_file, files
from watchdog.events import FileSystemEventHandler
import cos_uploader


class MyEventHandler(FileSystemEventHandler):
    client: CosS3Client
    bucket: str
    base_path: Path
    empty_file = Path(__file__).with_name("empty")

    def __init__(self, base_path: Path, secret_id: str, secret_key: str, region: str, bucket: str):
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
    def create_empty_file(self):
        """创建空文件用于创建文件夹——对象存储不支持文件夹"""
        if self.empty_file.is_file():
            if not self.empty_file.stat().st_size == 0:
                logger.warning("empty file size is not '0'")
                self.empty_file.unlink()
            else:
                return
        self.empty_file.write_bytes(b"")
        self.empty_file.chmod(0o444)

    def parse_local_and_remote_file(self, local: str) -> str:
        local_file_path = Path(local).resolve(strict=True)
        remote = local_file_path.relative_to(self.base_path).as_posix()
        if local_file_path.is_dir():
            remote_file_path = ""
            remote += "/"

    def on_any_event(self, event):
        logger.info(event)

    # 文件移动
    def on_moved(self, event):
        print(event)

    def on_created(self, event):
        local_file = Path(event.src_path)
        remote_file_path = self.file_path.relative_to(self.base_path)
        try:
            if local_file.is_file():
                self.client.upload_file(
                    Bucket=self.bucket,
                    Key=remote_file_path.as_posix(),
                    LocalFilePath=local_file,
                    EnableMD5=True,
                )
            else:
                with as_file(files(cos_uploader).joinpath("empty")) as f:
                    self.client.upload_file(
                        Bucket=self.bucket,
                        Key=remote_file_path.as_posix() + "/",
                        LocalFilePath=f,
                        EnableMD5=True,
                    )
        except (CosClientError, CosServiceError):
            logger.exception("upload failed")

    def on_deleted(self, event):
        print(event)

    def on_modified(self, event):
        print(event)
