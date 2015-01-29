from vdist.builder import Builder
from vdist.source import git

builder = Builder()

# add CentOS6 build
builder.add_build(
    name='myproject centos6 build',
    app='myproject',
    version='1.0',
    source=git(
        uri='http://yourgithost.internal/yourcompany/yourproject',
        branch='master'
    ),
    profile='centos6'
)

# add CentOS7 build
builder.add_build(
    name='myproject centos7 build',
    app='myproject',
    version='1.0',
    source=git(
        uri='http://yourgithost.internal/yourcompany/yourproject',
        branch='master'
    ),
    profile='centos7'
)

# add Ubuntu Trusty build
builder.add_build(
    name='myproject ubuntu build',
    app='myproject',
    version='1.0',
    source=git(
        uri='http://yourgithost.internal/yourcompany/yourproject',
        branch='master'
    ),
    profile='ubuntu-trusty'
)

# vdist will now build them all in parallel 
# on separate docker containers
builder.build()
