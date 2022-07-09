import filetype
import pytest
from loguru import logger


@pytest.mark.parametrize("resource", [r"D:\Users\80370454\Pictures\1027881260-01.jpeg"])
def test_image(resource):

    logger.info(filetype.guess(resource))
    logger.info(filetype.is_image(resource))
