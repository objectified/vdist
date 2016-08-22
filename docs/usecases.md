## Use cases
There are many situations where you would use vdist. If your application only
depended on packages from your system main repository then you could use
[fpm](https://github.com/jordansissel/fpm) directly but chances are that when
time passes further updates over your dependencies could break your application
(this is usually known as
[dependency hell](https://en.wikipedia.org/wiki/Dependency_hell))

That applies not only for external libraries your application uses but also for
the specific python interpreter you need to run your application.

To avoid *dependency hell* you should pack your application along with the
specific version of its dependencies (packages and needed interpreter) so they
are not affected by further updates. To create this bundle of your package and
its dependencies is where vdist comes to play.

Being aware of that, we have identified 4 main use cases for vdist:

- **Scenario 1** :: Your application includes a *setup.py* to be installed over
an specific compiled Python version.

- **Scenario 2** :: Your application does not include a *setup.py* but still
needs an specific compiled Python version.

- **Scenario 3** :: Your application includes a *setup.py* but uses a prebuilt
Python interpreter (maybe a custom Python package or the *vanilla* Python version
available in docker container you use for building process).

- **Scenario 4** :: Your application does not include a *setup.py* but uses a
prebuilt Python interpreter (maybe a custom Python package or the *vanilla*
Python version available in docker container you use for building process).

Whether you have a *setup.py* file or not is autodetected by vdist. If you don't want
to be in scenarios 1 or 3 just don't include *setup.py* file inside project given
to vdist.

###Scenarios 1 and 2
For scenarios 1 and 2 vdist is going to download from the official Python site
the specific interpreter version you need and compile it. Finally vdist is
going to install that compiled python interpreter in the folder (inside your
docker container) you gave in *python_basedir* parameter. If *python_basedir*
is not set, vdist installs compiled python in *app* folder inside */opt*.

Afterwards, if your project includes a *setup.py* (**scenario 1**) it will be run
(`python setup.py install`) using your compiled interpreter. That
means that your application will end being installed in the *site_packages*
folder of your compiled python distribution (if your setup.py creates entry
points they will appear in the *bin* folder of your compiled python distribution).
At packaging phase vdist will include only the compiled python folder inside the
generated package. If you have an entry point you could prepare a post install
script to link that entry point from your compiled python's *bin* folder to a
system wide folder like */usr/bin*. To include that post install script in
generated package just use *fpm_args* parameter.

An example configurarion for scenario 1 could be:
```python
builder_parameters = {
        "app": 'geolocate',
        "version": '1.3.0',
        "source": git(
                  uri='https://github.com/dante-signal31/geolocate',
                  branch='master'
                  ),
        "profile": 'ubuntu-trusty',
        "compile_python": True,
        "python_version": '3.4.3',
        "fpm_args": '--maintainer dante.signal31@gmail.com -a native --url '
                    'https://github.com/dante-signal31/geolocate --description '
                    '"This program accepts any text and searchs inside every IP'
                    ' address. With each of those IP addresses, '
                    'geolocate queries '
                    'Maxmind GeoIP database to look for the city and '
                    'country where'
                    ' IP address or URL is located. Geolocate is designed to be'
                    ' used in console with pipes and redirections along with '
                    'applications like traceroute, nslookup, etc.'
                    ' " --license BSD-3 --category net',
        "requirements_path": '/REQUIREMENTS.txt'
    }
```
This configuration would generate a package including only an */opt/geolocate*
folder with compiled python interpreter and geolocate application installed in
its *site-packages* folder. Entry points generated for geolocate will be placed
in *bin* folder of the compiled interpreter. Generated entry points will use
compiled intepreter and its packages so application will be entirely
self-sufficient on target system.


If your project doesn't include a *setup.py* (**scenario 2**) then your project
files will be stored in a folder different of the compiled python one. In that
case your application will end at *package_install_root* in a folder called
like *app* parameter. If *package_install_root* is not set then it will be the same
than *python_basedir*. That means that in this scenario vdist is going to include
two folders inside generated package: one for the python interpreter and one
for your application files. Your application files should be configured to use
correct path to call your compiled python interpreter on target system.

An example configurarion for scenario 2 could be:
```python
builder_parameters = {"app": 'jtrouble',
                      "version": '1.0.0',
                      "source": git(
                                uri='https://github.com/objectified/jtrouble',
                                branch='master'
                                ),
                      "profile": 'ubuntu-trusty',
                      "package_install_root": "/opt",
                      "python_basedir": "/opt/python",
                      "compile_python": True,
                      "python_version": '3.4.3', }
```
This configuration would generate a package including two folders: the one with
your application (*/opt/jtrouble*) and the one with your compiled python
interpreter (*/opt/python*).

###Scenarios 3 and 4
Scenarios 3 and 4 are respectively equivalent to scenarios 1 and 2. The main
difference is that while scenarios 1 and 2 download an interpreter from the
internet and compile it, scenarios 3 and 4 look for desired interpreter in the
docker container file system so that interpreter should be installed before
as a system package downloaded from a private repository or should be compiled
and included by default in a custom docker conatiner image. If you are in a
corporate enviroment you'll probably prefer this option because you'll probably
have enough resources to have your own private system package repository and
this way you can speed up greatly packaging process.

Appart from that difference between scenarios 3 and 4 is the same than between
scenarios 1 and 2.

An example configuration for **scenario 3** could be:
```python
builder_parameters = {
        "app": 'geolocate',
        "version": '1.3.0',
        "source": git(
            uri='https://github.com/dante-signal31/geolocate',
            branch='master'
        ),
        "profile": 'ubuntu-trusty',
        "compile_python": False,
        "python_version": '3.4.3',
        # Lets suppose custom python package is already installed and its root
        # folder is /usr.
        "python_basedir": '/usr',
        "fpm_args": '--maintainer dante.signal31@gmail.com -a native --url '
                    'https://github.com/dante-signal31/geolocate --description '
                    '"This program accepts any text and searchs inside'
                    ' every IP '
                    'address. With each of those IP addresses, '
                    'geolocate queries '
                    'Maxmind GeoIP database to look for the city and '
                    'country where'
                    ' IP address or URL is located. Geolocate is designed to be'
                    ' used in console with pipes and redirections along with '
                    'applications like traceroute, nslookup, etc.'
                    ' " --license BSD-3 --category net',
        "requirements_path": '/REQUIREMENTS.txt'
    }
```
Generated packaged will include just one folder: */usr/*

An example configuration for **scenario 4** may be:
```python
builder_parameters = {
        "app": 'jtrouble',
        "version": '1.0.0',
        "source": git(
            uri='https://github.com/objectified/jtrouble',
            branch='master'
        ),
        "profile": 'ubuntu-trusty',
        "compile_python": False,
        "python_version": '3.4.3',
        "python_basedir": '/usr',
    }
```
Generated package will include two folders: */usr* with python interpreter and
*/opt/app* folder with application inside. Note that */opt* is used for
application because *package_install_root* is not set so defaul value is used.

Please be aware that althoug examples for scenarios 3 and 4 include a very
specific *python_version* vdist only use its major version number (currently 2
or 3) to know whether call python or python3 executable at *python_basedir/bin*
folder.


