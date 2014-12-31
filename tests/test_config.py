import os
import pytest

from vdist.config import ApplicationConfig


@pytest.fixture
def localpath():
    return os.path.dirname(os.path.realpath(__file__))


def test_valid_config(localpath):
    config = ApplicationConfig()
    config.load(localpath + '/validconfig.yml')

    assert config.validate()


def test_invalid_config(localpath):
    config = ApplicationConfig()
    config.load(localpath + '/invalidconfig.yml')

    with pytest.raises(ValueError):
        config.validate()
