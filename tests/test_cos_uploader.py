import pytest
from cos_uploader import __version__
from cos_uploader.cli import app
from typer.testing import CliRunner


def test_version():
    assert __version__ == "0.0.0"
