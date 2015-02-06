import pytest

from vdist.builder import BuildProfile


def test_buildprofile_invalid_required_args():
    with pytest.raises(AttributeError):
        m = BuildProfile()


def test_buildprofile_valid_required_args():
    m = BuildProfile(
        profile_id='some_profile_id',
        docker_image='some_docker_image',
        script='foo.sh'
    )
    assert m.validate()


def test_buildprofile_insecure_registry_arg():
    m = BuildProfile(
        profile_id='some_profile_id',
        docker_image='some_docker_image',
        script='foo.sh',
        insecure_registry="true"
    )
    assert m.insecure_registry is True

    m = BuildProfile(
        profile_id='some_profile_id',
        docker_image='some_docker_image',
        script='foo.sh'
    )
    assert m.insecure_registry is False


def test_buildprofile_invalid_arg():
    with pytest.raises(AttributeError):
        m = BuildProfile(
            profile_id='some_profile_id',
            docker_image='some_docker_image',
            script='foo.sh',
            some_garbage='blah'
        )
