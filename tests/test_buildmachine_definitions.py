import pytest

from vdist.builder import BuildMachine


def test_buildmachine_invalid_required_args():
    with pytest.raises(AttributeError):
        m = BuildMachine()


def test_buildmachine_valid_required_args():
    m = BuildMachine(
        machine_id='some_machine_id',
        docker_image='some_docker_image',
        script='foo.sh'
    )
    assert m.validate()


def test_buildmachine_insecure_registry_arg():
    m = BuildMachine(
        machine_id='some_machine_id',
        docker_image='some_docker_image',
        script='foo.sh',
        insecure_registry="true"
    )
    assert m.insecure_registry


def test_buildmachine_invalid_arg():
    with pytest.raises(AttributeError):
        m = BuildMachine(
            machine_id='some_machine_id',
            docker_image='some_docker_image',
            script='foo.sh',
            some_garbage='blah'
        )
