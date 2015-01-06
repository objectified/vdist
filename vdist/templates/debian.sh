#!/bin/bash -x

# install fpm
apt-get update
apt-get dist-upgrade -y
apt-get install ruby-dev build-essential git python-virtualenv -y

gem install fpm

# install build dependencies
apt-get install -y {{build_deps|join(' ')}}

cd /dist

git clone {{git_url}}

cd {{app}}

virtualenv .

source bin/activate

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

if [ -f "setup.py" ]; then
    python setup.py install
fi

cd ..

fpm -s dir -t deb -n {{app}} -p /dist -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} {{app}}
