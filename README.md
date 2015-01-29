# vdist

vdist (Virtualenv Distribute) is a tool that lets you build OS packages from your Python applications, while aiming to build an isolated environment for your Python project by utilizing [virtualenv](https://virtualenv.pypa.io/en/latest/). This means that your application will not depend on OS provided packages of Python modules, including their versions. The idea is largely inspired by [this article](https://hynek.me/articles/python-app-deployment-with-native-packages/), so vdist basically implements the ideas outlined there. 

In short, the following principles are the most important motivation behind vdist:

- OS packages are a good idea; they make sure your application can be rolled out just like any other program, using the same tools (Salt, Ansible, Puppet, etc.)

- never let your application depend on packages provided by your OS

- build time dependencies are not runtime dependencies; no compilers etc. on your target system

- running your internal OS package mirrors and private PyPI repositories is a good idea


vdist takes an approach that's slightly different from the implementation examples found in the original article, but it's still very similar.

The main objective of vdist is to create clean, self contained OS packages from Python applications. This means that OS packages created with vdist contain your application, all Python dependencies needed by your application, and a Python interpreter. Every time vdist is creating a build, it does so on a clean OS image where all *build time* OS dependencies are installed from scratch before your application is being packaged on top of it. This means that the build machine will always be reverted to its original, clean state. To facilitate this, vdist uses Docker containers. By using so called "profiles", it's fairly easy to use your own custom Docker containers to be used by vdist when your project builds.

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
- `profile` :: the name of the profile to use for this specific build; its value should be a reflection of what gets put in the profiles.json file explained later
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

## Questions and Answers
*Q: Can I use vdist without running my own OS package mirrors, Docker registry and PyPI index?*
Yes you can. But your builds will be rather slow, and you won't have the advantages a private PyPI index will provide you with. It's not hard to set up, especially when using Docker.

*Q: Updating the Docker image takes a long time for every build. How can I speed this up?*
This will happen when you're using plain Docker images from the central Docker hub, which are probably not up to date with the latest packages. Also, vdist will try to install fpm as a ruby gem when it's not available yet. Installing ruby gems can take a long time. Next to this, vdist will by default compile a Python interpreter for you, which takes quite a while to build as well. For creating the most self contained builds with maximum speed, read the "Optimizing your build environment" section in the vdist documentation.

*Q: Why do you compile a Python interpreter from scratch? Is the OS provided interpreter not good enough?*
As with your module dependencies, you want to be sure that your application is as self contained as possible, using only those versions that you trust. The Python interpreter should be no exception to this. Also since we're using virtualenv, we need to make sure that the same interpreter that was used to set up the virtualenv can still be used at runtime. To have this guarantee, the interpreter is shipped.

*Q: Can vdist be used to create Docker images for my application, instead of OS packages?*
At the moment there is no builtin support for this, although I guess it could be done. When in high demand, I can look into it.

*Q: Why didn't you just plug into setuptools/distutils, or an existing build tool like PyBuilder?*
I could have done that, but it seemed that it would get a little messy. Having said that, I'm all ears when people want such a thing.
