# vdist

vdist (Virtualenv Distribute) is a tool that lets you build OS packages from your Python projects, while aiming to build an isolated environment for your Python project by utilizing [virtualenv](https://virtualenv.pypa.io/en/latest/). This means that your application will not depend on OS provided packages of Python modules, including their versions. The idea is largely inspired by [this article](https://hynek.me/articles/python-app-deployment-with-native-packages/), so vdist basically implements the ideas outlined there.

What vdist does is this: you create a Python file with some information about your project, vdist sets up a container for the specified target OS with the build time dependencies for the project, checks out your project inside the container, installs its Python dependencies in a virtualenv, optionally does some additional things and builds an OS package for you. This way, you know for sure that the Python modules needed by your application are installable on a clean installation of your target OS (including OS provided libraries, header files etc.) Also, you'll soon find out when something is missing on the target OS you want to deploy on.

By default, vdist will also compile and install a fresh Python interpreter for you, to be used by your application. This interpreter is used to create the aforementioned virtualenv, and will also be used when you deploy the resulting OS package. This allows you to choose the Python interpreter you want to use, instead of being tied to the version that is shipped with the OS you're deploying on.

Note that vdist is not meant to build Docker images for your project, it merely creates (nearly) self contained OS packages of your application, which you can then use to deploy on the target platform you told vdist to build for.

## How to install
Installing should be as easy as:
```
$ pip install vdist
```

## How to use
Inside your project, there are a few basic prerequisites for vdist to work.

1. Create a requirements.txt ('pip freeze > requirements.txt' inside a virtualenv should give you a good start); you probably already have one
2. Create a small Python file that actually uses the vdist module

Let's say we create a Python file called package.py, which would contain the following code:
```
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
    build_deps=[],
    runtime_deps=['ImageMagick-devel'],
    fpm_args='--license ScipyCentral'
)

builder.add_build(
    name='SciPyCentral builder :: ubuntu trusty',
    app='SciPyCentral',
    version='1.0',
    source=git(
        uri='https://github.com/scipy/SciPyCentral',
        branch='master'
    ),
    profile='ubuntu-trusty'
    build_deps=[],
    runtime_deps=['libimagemagick-dev'],
    fpm_args='--license ScipyCentral'
)

builder.build()
```
If all goes well, running this file as a Python program will build two OS packages (an RPM for CentOS 6 and a .deb package for Ubuntu Trusty Tahr) for a project called "ScipyCentral" (some Django application I found on Github). The two builds will be running in parallel threads, so you will see the build output of both threads at the same time, where the logging of each thread can be identified by the build name. Here's an explanation of the keyword arguments that can be given to `add_build()`:

### Required arguments:
- `name` :: the name of the build; this does not do anything in the build process itself, but is used in e.g. logs
- `app` :: the name of the application to build; this should also equal the project name in Git, and is used as the prefix for the filename of the resulting package
- `version` :: the version of the application; this is used when building the OS package both in the name and in its meta information
- `profile` :: the name of the profile to use for this specific build; its value should be a reflection of what gets put in the build_profiles.json file explained later
- `source` :: the argument that specifies how to get the source code to build from; the available source types are:
    * `git(uri=uri, branch=branch)`: this source type attempts to git clone by using the supplied arguments
    * `directory(path=path)`: this source type uses a local directory to build the project from, and uses no versioning data
    * `git_directory(path=path, branch=branch)`: this source type uses a git checkout in a local directory to build the project from; it checks out the supplied branch before building

### Optional arguments:
- `build_deps` :: a list of build time dependencies; these are the names of the OS packages that need to be present on the build machine before setting up and building the project
- `runtime_deps` :: a list of run time dependencies; these names are given to the resulting OS package as dependencies, so that they act as prerequisites when installing the final OS package
- `fpm_args` :: any extra arguments that are given to FPM (https://github.com/jordansissel/fpm) when the actual package is being built
- `working_dir` :: a subdirectory under your source tree that is to be regarded as the base directory; if set, only this directory is packaged, and the pip requirements are tried to be found here. This makes sense when you have a source repository with multiple projects under it.
- `requirements_path` :: the path to your pip requirements file, relative to your project root; this defaults to `/requirements.txt`
- `compile_python` :: indicates whether Python should be fetched from python.org, compiled and shipped for you; defaults to True
- `compile_python_version` :: the version of Python to compile and ship
- `python_basedir` :: specifies one of two things: 1) where Python can be found (your company might have a prepackaged Python) 2) where vdist should install the compiled Python distribution

## How to customize
It could well be that in your specific case, you need different steps to be taken to get to a deployable package. vdist by default is a bit naive: it checks for a requirements.txt and installs it using pip, and it also checks for a setup.py, on which it runs an install when present. Your situation might be a bit different. To solve this, vdist offers the ability to create mappings and templates for custom build profiles. First, create a directory called "templates" under your current working directory. In this directory, you place a script called "profiles.json". The profiles.json file might look like this:

```
{
    "centos6": {
        "docker_image": "yourcompany/centos6:latest",
        "script": "centos.sh"
    },
    "debian": {
        "docker_image": "yourcompany/debian:latest",
        "script": "debian.sh"
    }
}
```

In case it's not directly obvious, this configuration file defines 2 profiles: centos6 and debian. Each profile has 2 properties, called `docker_image` and `script`. The `docker_image` key indicates the name of the Docker image which will be pulled from the Docker repo by vdist. The `script` key indicates what script to load on the build machine to actually execute the build process. These scripts are treated as templates, and the build information you provide to vdist will be injected into these templates. You can take a look at vdist's own templates to get an idea of how they work, and how to create your own. They really are simple shell scripts that are treated as templates when a build executes. Custom shell scripts can be put in the templates directory alongside your profiles.json file. All parameters that are given by you when calling `add_build()` are injected into the template.

## How to contribute
I would certainly appreciate your help! Issues, feature requests and pull requests are more than welcome. I'm guessing I would need much more effort creating more profiles, but any help is appreciated!
