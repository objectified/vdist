from vdist.builder import Builder

builder = Builder()

builder.add_build(
    name='SciPyCentral builder :: centos6',
    app='SciPyCentral',
    version='1.0',
    git_url='https://github.com/scipy/SciPyCentral',
    build_machine_id='centos6'
)

builder.build()
