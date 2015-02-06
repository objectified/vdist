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

Note that vdist is not meant to build Docker images for your project, it merely creates (nearly) self contained OS packages of your application, which you can then use to deploy on the target OS you told vdist to build for. Also, vdist is not meant to create OS packages from Python libraries (for example, the ones you find on PyPI), but for applications. For a reasonably clear distinction between the two, I suggest you read [this article by Donald Stufft](https://caremad.io/2013/07/setup-vs-requirement/). Of course, your application can definitely include a number of libraries at build time (e.g. your Django application might well include all sorts of Python modules, but you won't use your Django application as a library).

## How to install
Installing should be as easy as:
```
$ pip install vdist
```

## How to use
Inside your project, there are a few basic prerequisites for vdist to work.

1. Create a requirements.txt ('pip freeze > requirements.txt' inside a virtualenv should give you a good start); you probably already have one
2. Create a small Python file that actually uses the vdist module

Here is a minimal example of how to use vdist to create an OS package of "yourapp" for Ubuntu Trusty. Create a file called package.py, which would contain the following code:

```
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

Here's a slightly more advanced example:

```
from vdist.builder import Builder
from vdist.source import git

builder = Builder()

# add CentOS6 build
builder.add_build(
    name='myproject :: centos6 build',
    app='myproject',
    version='1.0',
    source=git(
        uri='http://yourgithost.internal/yourcompany/yourproject',
        branch='master'
    ),
    profile='centos6'
)

# add Ubuntu build
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

If all goes well, running this file as a Python program will build two OS packages (an RPM for CentOS 6 and a .deb package for Ubuntu Trusty Tahr) for a project called "myproject". The two builds will be running in parallel threads, so you will see the build output of both threads at the same time, where the logging of each thread can be identified by the build name. Here's an explanation of the keyword arguments that can be given to `add_build()`:

### Required arguments:
- `app` :: the name of the application to build; this should also equal the project name in Git, and is used as the prefix for the filename of the resulting package
- `version` :: the version of the application; this is used when building the OS package both in the name and in its meta information
- `profile` :: the name of the profile to use for this specific build; its value should be a reflection of what gets put in the profiles.json file explained later
- `source` :: the argument that specifies how to get the source code to build from; the available source types are:
    * `git(uri=uri, branch=branch)`: this source type attempts to git clone by using the supplied arguments
    * `directory(path=path)`: this source type uses a local directory to build the project from, and uses no versioning data
    * `git_directory(path=path, branch=branch)`: this source type uses a git checkout in a local directory to build the project from; it checks out the supplied branch before building

### Optional arguments:
- `name` :: the name of the build; this does not do anything in the build process itself, but is used in e.g. logs; when omitted, the build name is a sanitized combination of the `app`, `version` and `profile` arguments
- `build_deps` :: a list of build time dependencies; these are the names of the OS packages that need to be present on the build machine before setting up and building the project
- `runtime_deps` :: a list of run time dependencies; these names are given to the resulting OS package as dependencies, so that they act as prerequisites when installing the final OS package
- `fpm_args` :: any extra arguments that are given to [fpm](https://github.com/jordansissel/fpm) when the actual package is being built
- `pip_args` :: any extra arguments that are given to pip when your pip requirements are being installed (a custom index url pointing to your private PyPI repository for example)
- `working_dir` :: a subdirectory under your source tree that is to be regarded as the base directory; if set, only this directory is packaged, and the pip requirements are tried to be found here. This makes sense when you have a source repository with multiple projects under it.
- `requirements_path` :: the path to your pip requirements file, relative to your project root; this defaults to `/requirements.txt`
- `compile_python` :: indicates whether Python should be fetched from python.org, compiled and shipped for you; defaults to True
- `compile_python_version` :: the version of Python to compile and ship, effective only when the `compile_python` setting is not False; defaults to the latest 2.7.\* version
- `python_basedir` :: specifies one of two things: 1) where Python can be found (your company might have a prepackaged Python) 2) where vdist should install the compiled Python distribution

Here's another, more customized example.

```
import os

from vdist.builder import Builder
from vdist.source import directory

# instantiate the builder while passing it a custom location for
# your profile definitions
profiles_path = os.path.dirname(os.path.abspath(__file__))

builder = Builder(profiles_dir='%s/deploy/profiles' % profiles_path)

# add CentOS6 build
builder.add_build(
    # name of the build
    name='myproject :: centos6 build',

    # name of the app (used for the package name)
    app='myproject',

    # the version; you might of course get this value from e.g. a file
    # or an environment variable set by your CI environment
    version='1.0',

    # base the build on a directory; this would make sense when executing
    # vdist in the context of a CI environment
    source=directory(path='/home/ci/projects/myproject'),

    # use the 'centos6' profile
    profile='centos6',

    # do not compile Python during packaging, a custom Python interpreter is
    # already made available on the build machine
    compile_python=False,

    # the location of your custom Python interpreter as installed by an
    # OS package
    python_basedir='/opt/yourcompany/python',

    # depend on an OS package called "yourcompany-python" which would contain
    # the Python interpreter; these are build dependencies, and are not
    # runtime dependencies
    build_deps=['yourcompany-python', 'gcc'],

    # specify OS packages that should be installed when your application is
    # installed
    runtime_deps=['yourcompany-python', 'imagemagick', 'ffmpeg'],

    # some extra arguments for fpm, in this case a postinstall script that
    # will run after your application will be installed (useful for e.g.
    # startup scripts, supervisor configs, etc.)
    fpm_args='--post-install deploy/centos6/postinstall.sh',

    # extra arguments to use when your pip requirements file is being installed
    # by vdist; a URL to your private PyPI server, for example
    pip_args='--index-url https://pypi.yourcompany.com/simple/',

    # find your pip requirements somewhere else instead of the project root
    requirements_path='deploy/requirements-prod.txt'
)

builder.build()
```
If you look in the vdist examples directory, you will find examples of more use cases.

## How to customize
It could well be that in your specific case, you need different steps to be taken to get to a deployable package. vdist by default is a bit naive: it checks for a requirements.txt and installs it using pip, and it also checks for a setup.py, on which it runs an install when present. Your situation might be a bit different. To solve this, vdist offers the ability to create custom build profiles. First, create a directory called "buildprofiles" under your project directory (location can be overridden by setting the `profiles_dir` argument on the Builder instance). In this directory, you place a script called "profiles.json". The profiles.json file might look like this:

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

This configuration file defines 2 profiles: centos6 and debian. Each profile has 2 properties, called `docker_image` and `script`. The `docker_image` key indicates the name of the Docker image which will be pulled from the Docker repo by vdist. The `script` key indicates what script to load on the build machine to actually execute the build process. These scripts are treated as templates, and the build information you provide to vdist will be injected into these templates. You can take a look at vdist's own templates to get an idea of how they work, and how to create your own. Custom shell scripts can be put in the profiles directory alongside your profiles.json file. All parameters that are given by you when calling `add_build()` are injected into the template. For Debian and CentOS/RHEL/Fedora images, vdist provides two scripts for you: `debian.sh` and `centos.sh`. You can refer to these scripts in your own custom profiles, while using your own Docker images.

## Optimizing your build environment
Using vdist out of the box would work fine if your context isn't all too demanding. When your demands are slightly higher (such as build speeds, continuous builds, etc.), I'd recommend getting a few things into place which can be used effectively in conjunction with vdist:
- an internal Docker registry; it's easy to set up (through using Docker)

- a private PyPI repository such as pypiserver or devpi;

- a Continuous Integration system such as Jenkins/Bamboo/etc.

- an internal OS package mirror (e.g. an APT or Yum mirror)

vdist would then be used in the final stage of a CI build, where it would fire up a preprovisioned Docker image (that resides on your private Docker registry), build your project, installs your internal modules from your private PyPI repository, and leaves the resulting OS packages as deliveries for your CI system.

To make a "fast" Docker image that can be used with vdist, make sure that:

- it's up to date

- it includes an already compiled Python interpreter (not your system's interpreter, since we prefer not to be dependent on it) that installs in e.g. /opt/yourcompany

- fpm is already installed (`gem install fpm` can take quite a while)

Once you've created a custom Docker image, you can refer to it in your `profiles.json` like you would normally do when using Docker:
```
{
    "my-custom-profile": {
        "docker_image": "docker-internal.yourcompany.com:5000/yourcompany/yourbuildmachine:latest",
        "script": "debian.sh"
    }
}
```

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

*Q: How does vdist compare to [Conda](http://conda.pydata.org)?*

Where vdist builds native OS packages for your target OS, Conda is a package management system. In that sense, Conda and vdist are fundamentally different things.

*Q: How does vdist compare to [Python Wheels](https://wheel.readthedocs.org/en/latest/)?*

If I'm not mistaken, wheels are primarily meant to create binary distributions of Python libraries. They won't necessarily help you with rolling out your applications. Wheels might be fetched from PyPI during a vdist build when available, (which is great, of course).

*Q: Any future plans for vdist?*

I have a few ideas, but I'm also very interested in hearing input for vdist from you. The following features jump to mind for now:

- smoke testing the installation of the resulting OS packages on a fresh Docker image

- the ability to commit a provisioned Docker image during the build run to a Docker registry

- integrating with (for example) PyBuilder

But like I said, I'm all open to ideas.

## How to contribute
I would certainly appreciate your help! Issues, feature requests and pull requests are more than welcome. I'm guessing I would need much more effort creating more profiles, but any help is appreciated!
