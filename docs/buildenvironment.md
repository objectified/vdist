## Optimizing your build environment
Using vdist out of the box would work fine if your context isn't all too demanding. When your demands are slightly higher (such as build speeds, continuous builds, etc.), I'd recommend getting a few things into place which can be used effectively in conjunction with vdist:
- an internal Docker registry; it's easy to set up (through using Docker)

- a private PyPI repository such as pypiserver or devpi;

- a Continuous Integration system such as Jenkins/Bamboo/etc.

- an internal OS package mirror (e.g. an APT or Yum mirror)

vdist would then be used in the final stage of a CI build, where it would fire up a preprovisioned Docker image (that resides on your private Docker registry), build your project, installs your internal modules from your private PyPI repository, and leaves the resulting OS packages as deliveries for your CI system.

To make a "fast" Docker image that can be used with vdist, make sure that:

- it's up to date (ideally by using a Configuration Management system)

- it includes an already compiled Python interpreter (not your system's interpreter, since we prefer not to be dependent on it) that installs in e.g. /opt/yourcompany

- it already includes your build time dependencies (which does not mean you should leave them out of the `build_deps` parameter)
 
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

