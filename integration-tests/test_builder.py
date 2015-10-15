import os
import subprocess
import tempfile

from vdist.builder import Builder
from vdist.source import git, git_directory, directory


def test_generate_deb_from_git():
    builder = Builder()
    builder.add_build(
        app='vdist-test-generate-deb-from-git',
        version='1.0',
        source=git(
            uri='https://github.com/objectified/vdist',
            branch='master'
        ),
        profile='ubuntu-trusty'
    )
    builder.build()

    homedir = os.path.expanduser('~')
    target_file = os.path.join(
        homedir,
        '.vdist',
        'dist',
        'vdist-test-generate-deb-from-git-1.0-ubuntu-trusty',
        'vdist-test-generate-deb-from-git_1.0_amd64.deb'
    )
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0


def test_generate_deb_from_git_suffixed():
    builder = Builder()
    builder.add_build(
        app='vdist-test-generate-deb-from-git-suffixed',
        version='1.0',
        source=git(
            uri='https://github.com/objectified/vdist.git',
            branch='master'
        ),
        profile='ubuntu-trusty'
    )
    builder.build()

    homedir = os.path.expanduser('~')
    target_file = os.path.join(
        homedir,
        '.vdist',
        'dist',
        'vdist-test-generate-deb-from-git-1.0-ubuntu-trusty',
        'vdist-test-generate-deb-from-git_1.0_amd64.deb'
    )
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0


def test_generate_deb_from_git_directory():
    tempdir = tempfile.gettempdir()
    checkout_dir = os.path.join(tempdir, 'vdist')

    git_p = subprocess.Popen(
        ['git', 'clone',
         'https://github.com/objectified/vdist',
         checkout_dir])
    git_p.communicate()

    builder = Builder()
    builder.add_build(
        app='vdist-test-generate-deb-from-git-dir',
        version='1.0',
        source=git_directory(
            path=checkout_dir,
            branch='master'
        ),
        profile='ubuntu-trusty'
    )
    builder.build()

    homedir = os.path.expanduser('~')
    target_file = os.path.join(
        homedir,
        '.vdist',
        'dist',
        'vdist-test-generate-deb-from-git-dir-1.0-ubuntu-trusty',
        'vdist-test-generate-deb-from-git-dir_1.0_amd64.deb'
    )
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0


def test_generate_deb_from_directory():
    tempdir = tempfile.gettempdir()
    checkout_dir = os.path.join(tempdir, 'vdist')

    git_p = subprocess.Popen(
        ['git', 'clone',
         'https://github.com/objectified/vdist',
         checkout_dir])
    git_p.communicate()

    builder = Builder()
    builder.add_build(
        app='vdist-test-generate-deb-from-dir',
        version='1.0',
        source=directory(
            path=checkout_dir,
        ),
        profile='ubuntu-trusty'
    )
    builder.build()

    homedir = os.path.expanduser('~')
    target_file = os.path.join(
        homedir,
        '.vdist',
        'dist',
        'vdist-test-generate-deb-from-dir-1.0-ubuntu-trusty',
        'vdist-test-generate-deb-from-dir_1.0_amd64.deb'
    )
    assert os.path.isfile(target_file)
    assert os.path.getsize(target_file) > 0
