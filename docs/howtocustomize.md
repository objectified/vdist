## How to customize
It could well be that in your specific case, you need different steps to be
taken to get to a deployable package. vdist by default is a bit naive: it
checks for a requirements.txt and installs it using pip, and it also checks
for a setup.py, on which it runs an install when present. Your situation might
be a bit different. To solve this, vdist offers the ability to create custom
build profiles. First, create a directory called `buildprofiles` under your
project directory (location can be overridden by setting the `profiles_dir`
argument on the Builder instance). In this directory, you place a script called
`profiles.json`. The `profiles.json` file might look like this:

```
{
    "centos7": {
        "docker_image": "yourcompany/centos7:latest",
        "script": "centos.sh"
    },
    "debian": {
        "docker_image": "yourcompany/debian:latest",
        "script": "debian.sh"
    }
}
```

This configuration file defines 2 profiles: `centos7` and `debian`. Each
profile has 2 properties, called `docker_image` and `script`. The
`docker_image` key indicates the name of the Docker image which will be
pulled from the Docker registry by vdist. This can also be an image on
your company's internal Docker registry, in which case the value for the
`docker_image` property would look like
"registry.company.internal:5000/user/project:version".
The `script` key indicates what script to load on the build machine to
actually execute the build process. These scripts are treated as
[Jinja2 templates](http://jinja.pocoo.org/), and the build information
you provide to vdist will be injected into these templates.

By default, vdist provides the scripts `centos.sh` and `debian.sh` as
generic templates for RHEL/CentOS/Fedora and Debian/Ubuntu based images,
so you can use those when defining your profile. You can take a look at
[the templates provided by vdist](https://github.com/objectified/vdist/tree/master/vdist/profiles)
to get an idea of how they work, and how to create your own. Custom shell
scripts can be put in the `buildprofiles` directory alongside your
profiles.json file. All parameters that are given by you when calling
`add_build()` are injected into the template, including a few more. You can
refer to these scripts in your own custom profiles, while using your own
Docker images. For example: your company provides a provisioned build image
based on Debian (custom Python interpreter package on board, regularly
maintained and all), and refers to "debian.sh" to perform the build.
