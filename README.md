# vdist

vdist (Virtualenv Distribute) is a tool that lets you build OS packages from your Python projects, while aiming to build an isolated environment for your Python project by utilizing [virtualenv](https://virtualenv.pypa.io/en/latest/). This means that your application will not depend on OS provided packages of Python modules, including their versions. The idea is largely inspired by [this article](https://hynek.me/articles/python-app-deployment-with-native-packages/), so vdist basically implements the ideas outlined there. 

What vdist does is this: you create a Python file with some information about your project, vdist sets up a container for the specified target OS with the build time dependencies for the project, checks out your project inside the container, installs its Python dependencies, optionally does some additional things and builds an OS package for you. This way, you know for sure that the Python modules needed by your application are installable on a clean installation of your target OS (including OS provided libraries, header files etc.) Also, you'll soon find out when something is missing on the target OS you want to deploy on.

By default, vdist will also compile and install a fresh Python interpreter for you, to be used by your application. This interpreter is used to create the aforementioned virtualenv, and will also be used when you deploy the resulting OS package.


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
    name='wand :: centos6',
    app='wand',
    version='1.0',
    git_url='https://github.com/dahlia/wand',
    build_deps=[],
    runtime_deps=['ImageMagick-devel'],
    build_machine='centos:centos6',
    fpm_args='--license Wand'
)

builder.add_build(
    name='wand :: ubuntu trusty',
    app='wand',
    version='1.0',
    git_url='https://github.com/dahlia/wand',
    build_deps=[],
    runtime_deps=['libmagickwand-dev'],
    build_machine='ubuntu:trusty',
    fpm_args='--license Wand'
)

builder.build()
```
If all goes well, running this file as a Python program will build two OS packages (an RPM for CentOS 6 and a .deb package for Ubuntu Trusty Tahr) for of a project called "Wand". Here's an explanation of the keyword arguments given to add_build():

- name :: the name of the build; this does not do anything in the build process itself, but is used in e.g. logs
- app :: the name of the application to build; this should also equal the project name in Git, and is used as the prefix for the filename of the resulting package
- version :: the version of the application; this is used when building the OS package both in the name and in its meta information
- git_url :: the URL that vdist will git clone the project from
- build_deps :: a list of build time dependencies; these are the names of the OS packages that need to be present on the build machine before setting up and building the project
- runtime_deps :: a list of run time dependencies; these names are given to the resulting OS package as dependencies, so that they act as prerequisites when installing the final OS package
- build_machine :: the name of the Docker image to set up the build machine for this specific build 
- fpm_args :: any extra arguments that are given to FPM (https://github.com/jordansissel/fpm) when the actual package is being built 

## How to customize
It could well be that in your specific case, you need different steps to be taken to get to a deployable package. vdist by default is a bit naive: it checks for a requirements.txt and installs it using pip, and it also checks for a setup.py, on which it runs an install when present. Your situation might be a bit different. To solve this, vdist offers the ability to create mappings and templates for custom build machines. First, create a directory called "templates" under your current working directory. In this directory, you place a script called "mappings.json". The mappings.json file might look like this:

```
{
    "web-machine": {
        flavor: "yourcompany/web:latest",
        template: "web_template.sh"  
    },
    "database-machine": {
        flavor: "yourcompany/database:latest",
        template: "database_template.sh"  
    }
}
```

In case it's not directly obvious, this mappings file defines 2 machines: web-machine and database-machine. Each machine has 2 properties, called "flavor" and "template". Flavor indicates the name of the Docker image, which will be pulled from the Docker repo by vdist (since only Docker is supported at the moment, we don't need to be explicit about it). The "template" key indicates what script to load on the build machine to actually execute the build process. You can take a look at vdist's own templates to get an idea of how they work, and how to create your own. They really are simple shell scripts, that are used as templates so that specific build information can be injected at runtime. All parameters that are given by you when calling add_build() are injected into the template. 
