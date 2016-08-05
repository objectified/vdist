Before installing vdist, it is important that you have the Docker daemon
running. I recommend getting the latest version of Docker to use with vdist.

Installing vdist is as easy as this:
```
$ pip install vdist
```

Alternatively, you can clone the source directly from Github and install its
dependencies via pip. When doing that, I recommend using virtualenv. For
example:

```
$ git clone https://github.com/objectified/vdist
$ cd vdist
$ virtualenv .
$ . bin/activate
$ pip install -r requirements.txt
```
