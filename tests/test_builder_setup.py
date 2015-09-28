import pytest

from vdist.builder import Builder, NoBuildsFoundException


def test_builder_nobuilds():
    b = Builder()

    with pytest.raises(NoBuildsFoundException):
        b.build()


def test_internal_profile_loads():
    b = Builder()

    profiles = b.get_available_profiles()

    internal_profile_ids = ['ubuntu-trusty', 'centos6', 'debian-wheezy']

    for profile_id in internal_profile_ids:
        assert profile_id in profiles
