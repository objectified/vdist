import pytest

from vdist.builder import Builder, NoBuildsFoundException


def test_builder_nobuilds():
    b = Builder()

    with pytest.raises(NoBuildsFoundException):
        b.build()
