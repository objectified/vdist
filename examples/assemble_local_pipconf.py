"""
This example shows how you can tell vdist to use
your local pip configuration (~/.pip/pip.conf) when
building. This is useful when you're using an internal
PyPI index (highly recommended)
"""
from vdist.builder import Builder
from vdist.source import git

builder = Builder()

builder.add_build(
    name='my great project',
    app='myproject',
    version='1.0',
    source=git(
        uri='https://github.com/someuser/someproject',
        branch='your-release-branch'
    ),
    profile='ubuntu-trusty',
    # this means that during the build run, vdist will
    # copy your pip config (~/.pip/pip.conf) to the Docker
    # container it uses to build the OS package, so that you
    # can use your internal modules as pip dependencies in
    # your requirements.txt / setup.py
    use_local_pip_conf=True
)

builder.build()
