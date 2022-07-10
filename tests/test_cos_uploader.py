import pytest
from cos_uploader import __version__
from cos_uploader.cli import app
from typer.testing import CliRunner


@pytest.fixture(scope="session")
def runner():
    return CliRunner()


def test_version():
    assert __version__ == "0.0.0"

@pytest.mark.timeout(3)
def test_simple(runner: CliRunner, tmp_path):
    result = runner.invoke(app, str(tmp_path))
    assert result.exit_code == 0
