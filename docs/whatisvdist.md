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


