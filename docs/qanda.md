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

