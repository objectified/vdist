# vdist

Welcome to the home of vdist, a tool that lets you create OS packages from your Python applications in a clean and self contained manner. It uses [virtualenv](https://virtualenv.pypa.io/en/latest/), [Docker](https://www.docker.com/) and [fpm](https://github.com/jordansissel/fpm) under the hood, and it uses [Jinja2](http://jinja.pocoo.org/docs/dev/) to render its templates (shell scripts) for each individual target OS.

The source for vdist is available under the MIT license and can be found on [Github](https://github.com/objectified/vdist)

vdist is currently in alpha stage, but it should work just fine. If you find any issues, please report issues or submit pull requests via Github.
