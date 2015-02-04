from vdist.builder import Build
from vdist.source import git, directory, git_directory


def test_build_projectroot_from_uri():
    build = Build(
        name='my build',
        app='myapp',
        version='1.0',
        source=git(
            uri='https://github.com/objectified/vdist',
            branch='release-1.0'
        ),
        profile='ubuntu-trusty'
    )
    assert build.get_project_root_from_source() == 'vdist'


def test_build_projectroot_from_directory():
    build = Build(
        name='my build',
        app='myapp',
        version='1.0',
        source=directory(path='/var/tmp/vdist'),
        profile='ubuntu-trusty'
    )
    assert build.get_project_root_from_source() == 'vdist'


def test_build_projectroot_from_git_directory():
    build = Build(
        name='my build',
        app='myapp',
        version='1.0',
        source=git_directory(
            path='/var/tmp/vdist',
            branch='release-1.0'
        ),
        profile='ubuntu-trusty'
    )
    assert build.get_project_root_from_source() == 'vdist'


def test_build_get_safe_dirname():
    build = Build(
        name='my build',
        app='myapp-foo @#^&_',
        version='1.0',
        source=git_directory(
            path='/var/tmp/vdist',
            branch='release-1.0'
        ),
        profile='ubuntu-trusty'
    )
    assert build.get_safe_dirname() == 'myapp-foo______-1.0-ubuntu-trusty'
