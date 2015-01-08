#!/bin/bash -x
PYTHON_VERSION="2.7.9"

# install fpm
apt-get update
apt-get dist-upgrade -y
apt-get install ruby-dev build-essential git python-virtualenv curl -y

gem install fpm

# install build dependencies
{% if build_deps %}
apt-get install -y {{build_deps|join(' ')}}
{% endif %}

# install python prerequisites 
apt-get build-dep python -y
apt-get install libssl-dev -y

# compile and install python
cd /var/tmp
curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
tar xzvf Python-$PYTHON_VERSION.tgz
cd Python-$PYTHON_VERSION
./configure --prefix=/opt/vdist-python
make && make install

cd /opt

git clone {{git_url}}

cd {{app}}

rm -rf .git

virtualenv -p /opt/vdist-python/bin/python .

source bin/activate

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

if [ -f "setup.py" ]; then
    python setup.py install
fi

cd ..

fpm -s dir -t deb -n {{app}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} /opt 
