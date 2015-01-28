"""
This example shows how you can use vdist to use a subdirectory
under your source tree to use as the base for your OS package
You will still be able to use git branching to point to the right
release, since vdist will first checkout the parent, and set apart
the subdirectory after switching to the right branch
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
    # specify 'subapp' as the working directory for this build;
    # this means that only the subapp directory will be built and
    # packaged
    # This also means that vdist will look for a pip requirements
    # file in this directory
    working_dir='subapp'
)

builder.build()
