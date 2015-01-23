# vdist

vdist (Virtualenv Distribute) is a tool that lets you build OS packages from your Python projects, while aiming to build an isolated environment for your Python project by utilizing [virtualenv](https://virtualenv.pypa.io/en/latest/). This means that your application will not depend on OS provided packages of Python modules, including their versions. The idea is largely inspired by [this article](https://hynek.me/articles/python-app-deployment-with-native-packages/), so vdist basically implements the ideas outlined there. 

What vdist does is this: you create a Python file with some information about your project, vdist sets up a container for the specified target OS with the build time dependencies for the project, checks out your project inside the container, installs its Python dependencies, optionally does some additional things and builds an OS package for you. This way, you know for sure that the Python modules needed by your application are installable on a clean installation of your target OS (including OS provided libraries, header files etc.) Also, you'll soon find out when something is missing on the target OS you want to deploy on.

By default, vdist will also compile and install a fresh Python interpreter for you, to be used by your application. This interpreter is used to create the aforementioned virtualenv, and will also be used when you deploy the resulting OS package.

Note that vdist is not meant to build Docker images for your project, it merely creates (nearly) self contained OS packages of your application, which you can then use to deploy on the target platform you told vdist to build for.

## How to install 
Installing should be as easy as:
```
$ pip install vdist
```

## How to use
Inside your project, there are a few basic prerequisites for vdist to work.

1. Create a requirements.txt ('pip freeze > requirements.txt' inside a virtualenv should give you a good start)
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
    build_machine_id='centos6'
    build_deps=[],
    runtime_deps=['ImageMagick-devel'],
    build_machine_id='centos6',
    fpm_args='--license ScipyCentral'
)

builder.add_build(
    name='SciPyCentral builder :: ubuntu trusty',
    app='SciPyCentral',
    version='1.0',
    git_url='https://github.com/scipy/SciPyCentral',
    build_machine_id='ubuntu-trusty'
    build_deps=[],
    runtime_deps=['libimagemagick-dev'],
    build_machine_id='ubuntu-trusty',
    fpm_args='--license ScipyCentral'
)

builder.build()
```
If all goes well, running this file as a Python program will build two OS packages (an RPM for CentOS 6 and a .deb package for Ubuntu Trusty Tahr) for a project called "ScipyCentral" (some Django application I found on Github). The two builds will be running in parallel threads, so you will see the build output of both threads at the same time, where the logging of each thread can be identified by the build name. Here's an explanation of the keyword arguments given to add_build():

- name :: the name of the build; this does not do anything in the build process itself, but is used in e.g. logs
- app :: the name of the application to build; this should also equal the project name in Git, and is used as the prefix for the filename of the resulting package
- version :: the version of the application; this is used when building the OS package both in the name and in its meta information
- git_url :: the URL that vdist will git clone the project from
- build_deps :: a list of build time dependencies; these are the names of the OS packages that need to be present on the build machine before setting up and building the project
- runtime_deps :: a list of run time dependencies; these names are given to the resulting OS package as dependencies, so that they act as prerequisites when installing the final OS package
- build_machine_id :: the id of the Docker image to set up the build machine for this specific build; this id should be a reflection of what gets put in the build_machines.json file explained later
- fpm_args :: any extra arguments that are given to FPM (https://github.com/jordansissel/fpm) when the actual package is being built 

## How to customize
It could well be that in your specific case, you need different steps to be taken to get to a deployable package. vdist by default is a bit naive: it checks for a requirements.txt and installs it using pip, and it also checks for a setup.py, on which it runs an install when present. Your situation might be a bit different. To solve this, vdist offers the ability to create mappings and templates for custom build machines. First, create a directory called "templates" under your current working directory. In this directory, you place a script called "build_machines.json". The build_machines.json file might look like this:

```
{
    "web-machine": {
        "docker_image": "yourcompany/web:latest",
        "script": "web_template.sh"  
    },
    "database-machine": {
        "docker_image": "yourcompany/database:latest",
        "script": "database_template.sh"  
    }
}
```

In case it's not directly obvious, this configuration file defines 2 machines: web-machine and database-machine. Each machine has 2 properties, called "docker_image" and "script". The "docker_image" key indicates the name of the Docker image which will be pulled from the Docker repo by vdist. The "script" key indicates what script to load on the build machine to actually execute the build process. These scripts are treated as templates, and the build information you provide to vdist will be injected into these templates. You can take a look at vdist's own templates to get an idea of how they work, and how to create your own. They really are simple shell scripts that are treated as templates when a build executes. Custom shell scripts can be put in the templates directory alongside your build_machines.json file. All parameters that are given by you when calling add_build() are injected into the template. 

## How to contribute
I would certainly appreciate your help! Issues, feature requests and pull requests are more than welcome. I'm guessing I would need much more effort creating more deployment templates, but any help is appreciated!
