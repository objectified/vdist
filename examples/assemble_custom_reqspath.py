"""
This example shows how you can point to an alternative
pip requirements file to use when building your OS package
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
    # path will be used relative to your checkout directory
    # by default vdist will look for $checkout/requirements.txt
    requirements_path='/requirements/production.txt'
)

builder.build()
