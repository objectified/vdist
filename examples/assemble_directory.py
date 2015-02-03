from vdist.builder import Builder
from vdist.source import directory, git_directory

builder = Builder()

# build from a local directory
builder.add_build(
    name='my directory based build',
    app='myproject',
    version='1.0',
    source=directory(
        path='/home/user/dev/yourproject'
    ),
    profile='centos6'
)

# or, build from a git repo *inside* a local directory 
builder.add_build(
    name='my directory based build',
    app='myproject',
    version='1.0',
    source=git_directory(
        path='/home/user/dev/anotherproject',
        branch='your-release-branch'
    ),
    profile='centos6'
)

# .. and build them in parallel
builder.build()
