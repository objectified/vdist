# vdist

Welcome to the home of vdist, a tool that lets you create OS packages from your Python applications in a clean and self contained manner. It uses [virtualenv](https://virtualenv.pypa.io/en/latest/), [Docker](https://www.docker.com/) and [fpm](https://github.com/jordansissel/fpm) under the hood, and it uses [Jinja2](http://jinja.pocoo.org/docs/dev/) to render its templates (shell scripts) for each individual target OS.

The source for vdist is available under the MIT license and can be found on [Github](https://github.com/objectified/vdist)

vdist is currently in alpha stage, but it should work just fine. If you find any issues, please report issues or submit pull requests via Github.

Here's a quickstart to give you an idea of how to use vdist, once you're set up.

```
from vdist.builder import Builder
from vdist.source import git

builder = Builder()

builder.add_build(
    app='yourapp',
    version='1.0',
    source=git(
        uri='https://github.com/you/yourapp',
        branch='release-1.0'
    ),
    profile='ubuntu-trusty',
    build_deps=['libpq-dev'],
    runtime_deps=['libcurl3']
)

builder.build()
```

Running the above would do this:

- set up a Docker container running Ubuntu Trusty Tahr

- install the OS packages listed in `build_deps` (only libpq-dev in this case)

- git clone the repository at https://github.com/you/yourapp

- checkout the branch 'release-1.0'

- set up a virtualenv for the checked out application

- install your application's dependencies from requirements.txt

- wrap the virtualenv in a package called `yourapp-1.0.deb` which includes a dependency on the OS packages listed in `runtime_deps`


Similarly, the same build for CentOS 6 would look like this.

```
from vdist.builder import Builder
from vdist.source import git

builder = Builder()

builder.add_build(
    app='yourapp',
    version='1.0',
    source=git(
        uri='https://github.com/you/yourapp',
        branch='release-1.0'
    ),
    profile='centos6',
    build_deps=['postgresql-devel'],
    runtime_deps=['libcurl3']
)

builder.build()
```

Read more about what vdist can do [here](http://vdist.readthedocs.org/en/latest/howtouse/)
