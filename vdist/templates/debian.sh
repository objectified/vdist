#!/bin/bash -x
PYTHON_VERSION="2.7.9"

# fail on error
set -e

# install fpm
apt-get update
apt-get install ruby-dev build-essential git python-virtualenv curl libssl-dev libsqlite3-dev libgdbm-dev libreadline-dev libbz2-dev libncurses5-dev tk-dev -y

# only install when needed, to save time with 
# pre-provisioned containers
if [ ! -f /usr/bin/fpm ]; then
    gem install fpm
fi

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

{% if source.type == 'git' %}

    git clone {{source.uri}}
    cd {{app}}
    git checkout {{source.branch}}
    rm -rf .git

{% elif source.type == 'directory' %}

    cp -r /opt/scratch/{{app}} .
    cd /opt/{{app}}

{% else %}

    echo "invalid source type, exiting."
    exit 1

{% endif %}

{% if use_local_pypirc %}

    cp /opt/scratch/.pypirc ~

{% endif %}


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

chown -R {{local_uid}}:{{local_gid}} /opt
