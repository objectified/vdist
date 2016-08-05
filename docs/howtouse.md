## How to use
Inside your project, there are a few basic prerequisites for vdist to work.

1. Create a requirements.txt ('pip freeze > requirements.txt' inside a
virtualenv should give you a good start); you probably already have one
2. Create a small Python file that actually uses the vdist module

Here is a minimal example of how to use vdist to create an OS package of
"yourapp" for Ubuntu Trusty. Create a file called package.py, which would
contain the following code:

```python
from vdist.builder import Builder
from vdist.source import git

builder = Builder()

builder.add_build(
    app='yourapp',
    version='1.0',
    source=git(
        uri='https://github.com/you/yourapp',
        branch='master'
    ),
    profile='ubuntu-trusty'
)

builder.build()
```

Here is what it does: vdist will build an OS package called 'yourapp-1.0.deb'
from a Git repo located at https://github.com/you/yourapp, from branch 'master'
using the vdist profile 'ubuntu-trusty' (more on vdist profiles later).
While doing so, it will download and compile a Python interpreter, set up a
virtualenv for your application, and installs your application's dependencies
into the virtualenv. The whole resulting virtualenv will be wrapped up in a
package, and is the end result of the build run. Here's an example creating a
build for two OS flavors at the same time:

```python
from vdist.builder import Builder
from vdist.source import git

builder = Builder()

# Add CentOS7 build
builder.add_build(
    name='myproject :: centos7 build',
    app='myproject',
    version='1.0',
    source=git(
        uri='http://yourgithost.internal/yourcompany/yourproject',
        branch='master'
    ),
    profile='centos7'
)

# Add Ubuntu build
builder.add_build(
    name='myproject :: ubuntu trusty build',
    app='myproject',
    version='1.0',
    source=git(
        uri='http://yourgithost.internal/yourcompany/yourproject',
        branch='master'
    ),
    profile='ubuntu-trusty'
)

builder.build()
```

If all goes well, running this file as a Python program will build two OS
packages (an RPM for CentOS 7 and a .deb package for Ubuntu Trusty Tahr)
for a project called "myproject". The two builds will be running in parallel
threads, so you will see the build output of both threads at the same time,
where the logging of each thread can be identified by the build name.
Here's an explanation of the keyword arguments that can be given to
`add_build()`:

### Required arguments:
- `app` :: the name of the application to build; this should also equal the
project name in Git, and is used as the prefix for the filename of the
resulting package
- `version` :: the version of the application; this is used when building the
OS package both in the name and in its meta information
- `profile` :: the name of the profile to use for this specific build; its
value should be one of two things:
    * a vdist built-in profile (currently `centos7`, `ubuntu-trusty` and
    `debian-wheezy` are available)
    * a custom profile that you create yourself; see
    [How to customize](http://vdist.readthedocs.org/en/latest/howtocustomize)
    for instructions
- `source` :: the argument that specifies how to get the source code to build
from; the available source types are:
    * `git(uri=uri, branch=branch)`: this source type attempts to git clone by
    using the supplied arguments
    * `directory(path=path)`: this source type uses a local directory to build
    the project from, and uses no versioning data
    * `git_directory(path=path, branch=branch)`: this source type uses a git
    checkout in a local directory to build the project from; it checks out the
    supplied branch before building

### Optional arguments:
- `name` :: the name of the build; this does not do anything in the build
process itself, but is used in e.g. logs; when omitted, the build name is a
sanitized combination of the `app`, `version` and `profile` arguments.
- `build_deps` :: a list of build time dependencies; these are the names of
the OS packages that need to be present on the build machine before setting
up and building the project.
- `runtime_deps` :: a list of run time dependencies; these names are given to
the resulting OS package as dependencies, so that they act as prerequisites
when installing the final OS package.
- `custom_filename` :: specifies a custom filename to use when generating
the OS package; within this filename, references to environment variables
may be used when put in between curly braces
(e.g. `foo-{ENV_VAR_ONE}-bar-{ENV_VAR_TWO}.deb`); this is useful when for
example your CI system passes values such as the build number and so on.
- `fpm_args` :: any extra arguments that are given to
[fpm](https://github.com/jordansissel/fpm) when the actual package is being
built.
- `pip_args` :: any extra arguments that are given to pip when your pip
requirements are being installed (a custom index url pointing to your private
PyPI repository for example).
- `package_install_root`:: Base directory were this package is going to be
installed in target system (defaults to '*python_basedir*').
- `package_tmp_root` :: Temporal folder used in docker container to build your
package (defaults to '*/tmp*').
- `working_dir` :: a subdirectory under your source tree that is to be regarded
as the base directory; if set, only this directory is packaged, and the pip
requirements are tried to be found here. This makes sense when you have a
source repository with multiple projects under it.
- `python_basedir` :: specifies one of two things: 1) where Python can be
found (your company might have a prepackaged Python already installed on your
custom docker container) 2) where vdist should install the compiled Python
distribution on your docker container. Read different [use cases](usecases.md)
to understand the nuance. Defaults to '*/opt*'.
- `compile_python` :: indicates whether Python should be fetched from
python.org, compiled and shipped for you; defaults to *True*. If not *True* then
'*python_basedir*' should point to a python distribution already installed in
docker container.
- `python_version` :: specifies two things: 1) if '*compile_python*' is *True*
then it means the exact python version that should be downloaded and compiled.
2) if '*compile_python*' is *False* then only mayor version number is considered
(currently 2 or 3) and latest available python distribution of that mayor
version is searched (in given '*python_basedir*' of your docker container) to be
used. Defaults to '*2.7.9*'.
- `requirements_path` :: the path to your pip requirements file, relative to
your project root; this defaults to `*/requirements.txt*`.

Here's another, more customized example.

```python
import os

from vdist.builder import Builder
from vdist.source import directory

# Instantiate the builder while passing it a custom location for
# your profile definitions
profiles_path = os.path.dirname(os.path.abspath(__file__))

builder = Builder(profiles_dir='%s/deploy/profiles' % profiles_path)

# Add CentOS7 build
builder.add_build(
    # Name of the build
    name='myproject :: centos6 build',

    # Name of the app (used for the package name)
    app='myproject',

    # The version; you might of course get this value from e.g. a file
    # or an environment variable set by your CI environment
    version='1.0',

    # Base the build on a directory; this would make sense when executing
    # vdist in the context of a CI environment
    source=directory(path='/home/ci/projects/myproject'),

    # Use the 'centos7' profile
    profile='centos7',

    # Do not compile Python during packaging, a custom Python interpreter is
    # already made available on the build machine
    compile_python=False,

    # The location of your custom Python interpreter as installed by an
    # OS package (usually from a private package repository) on your
    # docker container.
    python_basedir='/opt/yourcompany/python',
    # As python_version is not given, vdist is going to assume your custom
    # package is a Python 2 interpreter, so it will call 'python'. If your
    # package were a Python 3 interpreter then you should include a
    # python_version='3' in this configuration to make sure that vdist looks
    # for a 'python3' executable in 'python_basedir'.

    # Depend on an OS package called "yourcompany-python" which would contain
    # the Python interpreter; these are build dependencies, and are not
    # runtime dependencies. You docker container should be configured to reach
    # your private repository to get "yourcompany-python" package.
    build_deps=['yourcompany-python', 'gcc'],

    # Specify OS packages that should be installed when your application is
    # installed
    runtime_deps=['yourcompany-python', 'imagemagick', 'ffmpeg'],

    # Some extra arguments for fpm, in this case a postinstall script that
    # will run after your application will be installed (useful for e.g.
    # startup scripts, supervisor configs, etc.)
    fpm_args='--post-install deploy/centos7/postinstall.sh',

    # Extra arguments to use when your pip requirements file is being installed
    # by vdist; a URL to your private PyPI server, for example
    pip_args='--index-url https://pypi.yourcompany.com/simple/',

    # Find your pip requirements somewhere else instead of the project root
    requirements_path='deploy/requirements-prod.txt',
    
    # Specify a custom filename, including the values of environment variables
    # to build up the filename; these can be set by e.g. a CI system
    custom_filename='myapp-{GIT_TAG}-{CI_BUILD_NO}-{RELEASE_NAME}.deb'
)

builder.build()
```
You can read some examples with the main vdist [use cases](usecases.md) we have
identified. Additionally if you look in the
[vdist examples directory](https://github.com/objectified/vdist/tree/master/examples),
you will find even more examples.

There are cases where you want to influence the way vdist behaves in your
environment. This can be done by passing additional parameters to the vdist
Builder constructor. Here's an example:

```
import os

from vdist.builder import Builder
from vdist.source import git

profiles_dir = os.path.join(os.path.dirname(__file__), 'myprofiles')

builder = Builder(
    profiles_dir=profiles_dir,
    machine_logs=False
)

builder.add_build(
    app='myapp',
    source=git(uri='https://github.com/foo/myproject', branch='myrelease'),
    version='1.0',
    profile='ubuntu-trusty'
)

builder.build()
```

In the above example, two things are customized for this build run:

1. vdist looks at a different directory for finding your custom profiles

2. the logging of what happens on the Docker image is turned off
