from vdist.builder import Builder
from vdist.source import git

builder = Builder()

builder.add_build(
    name='my project build',
    app='myproject',
    version='1.0',
    source=git(
        uri='https://github.com/someuser/someproject',
        branch='your-release-branch'
    ),
    profile='ubuntu-trusty',
    # Tell vdist that we need the OS packages "ffmpeg" and "imagemagick"
    # on the system this application gets deployed
    # These packages will be made dependencies of the resulting OS package
    runtime_deps=['ffmpeg', 'imagemagick'],
    # tell vdist that on the machine that is used for building this project,
    # we will need the OS packages "libimagemagick-dev" and "libmysqlclient-dev"
    # before we start building
    build_deps=['libimagemagick-dev', 'libmysqlclient-dev']
)

builder.build()
