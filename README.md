# vdist

vdist (Virtualenv Distribute) is a tool that lets you build OS packages from your Python projects, while aiming to build an isolated environment for your Python project by utilizing [virtualenv](https://virtualenv.pypa.io/en/latest/). This means that your application will not depend on OS provided packages of Python modules, including their versions. The idea is largely inspired by [this article](https://hynek.me/articles/python-app-deployment-with-native-packages/), so vdist basically implements the ideas outlined there. What vdist does is this: you create a Python file with some information about your project, vdist sets up a container for the specified target OS with the build time dependencies for the project, checks out your project inside the container, installs its Python dependencies, optionally does some additional things and builds an OS package for you. This way, you know for sure that the Python modules needed by your application are installable on your target OS (including OS provided libraries, header files etc.) Also, you'll soon find out when something is missing on the target OS you want to deploy on.

## How to install 
Installing should be as easy as:
$ pip install vdist

## How to use
Inside your project, there are a few basic prerequisites for vdist to work.
1. Create a requirements.txt ('pip freeze > requirements.txt' inside a virtualenv should give you a good start)
2. Create a small Python file that actually uses the vdist module
Let's say we create a Python file called package.py, which would contain the following code:
```
from vdist.builder import Builder

builder = Builder()

builder.add_build(
    name='Selmon :: CentOS 6 Build',
    app='selmon',
    version='1.0',
    git_url='https://github.com/objectified/selmon',
    build_deps=['gcc', 'python-devel'],
    runtime_deps=['libmysqlclient'],
    build_machine={'driver': 'docker', 'flavor': 'centos:centos6'},
    fpm_args='--license Apache'
)

builder.add_build(
    name='Selmon :: Ubuntu Build',
    app='selmon',
    version='1.0',
    git_url='https://github.com/objectified/selmon',
    build_deps=['build-essential', 'python-dev'],
    runtime_deps=['libmysqlclient'],
    build_machine={'driver': 'docker', 'flavor': 'ubuntu:trusty'},
    fpm_args='--license Apache'
)

builder.build()
```
If all goes well, running this file as a Python program will build two OS packages (an RPM for CentOS 6 and a .deb package for Ubuntu Trusty Tahr) for of a project called "selmon".
