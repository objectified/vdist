"""
This example shows how you can use vdist with your
own package of the Python interpreter; you might want
this when you do not want vdist to compile Python
every time your project builds, and you've got Python
available as a custom OS package (something I'd highly
recommend for cross platform stability and packaging
speed)
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
    # tell vdist not to compile Python
    compile_python=False,
    # point to the basedir your custom Python is installed in
    # vdist will look for $basedir/bin/python
    python_basedir='/opt/mycompany/python',
    # provide your custom Python OS package as a build dependency
    build_deps=['mycompany-python'],
    # provide your custom Python OS package as a runtime dependency
    runtime_deps=['mycompany-python']
)

builder.build()
