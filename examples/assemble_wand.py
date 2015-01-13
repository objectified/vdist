from vdist.builder import Builder

# instantiate the vdist builder
builder = Builder()

# create an Ubuntu package for Wand
builder.add_build(
    name='Wand Ubuntu',
    app='wand',
    git_url='https://github.com/dahlia/wand',
    version='1.0',
    build_machine='ubuntu-trusty',
    build_deps=[],
    runtime_deps=['libmagickwand-dev']
)

# create a CentOS 6 package for Wand
builder.add_build(
    name='Wand CentOS',
    app='selmon',
    git_url='https://github.com/dahlia/wand',
    version='1.0',
    build_machine='centos6',
    runtime_deps=['ImageMagick-devel']
)

# run above builds in parallel
builder.build()
