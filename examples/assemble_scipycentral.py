from vdist.builder import Builder
from vdist.source import git

builder = Builder()

builder.add_build(
    name='SciPyCentral builder :: centos6',
    app='SciPyCentral',
    version='1.0',
    source=git(
        uri='https://github.com/scipy/SciPyCentral',
        branch='master'
    ),
    profile='centos6'
)

builder.build()
