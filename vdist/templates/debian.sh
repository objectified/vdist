#!/bin/bash -x
PYTHON_VERSION="2.7.9"
CUSTOM_PYTHON_PATH="/opt/vdist-python"

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
./configure --prefix=$CUSTOM_PYTHON_PATH
make && make install

cd /opt

{% if source.type == 'git' %}

    git clone {{source.uri}}
    cd {{basename}}
    git checkout {{source.branch}}

{% elif source.type in ['directory', 'git_directory'] %}

    cp -r /opt/scratch/{{basename}} .
    cd /opt/{{basename}}

    {% if source.type == 'git_directory' %}
        git checkout {{source.branch}}
    {% endif %}

{% else %}

    echo "invalid source type, exiting."
    exit 1


{% endif %}

{% if use_local_pip_conf %}
    cp -r /opt/scratch/.pip ~
{% endif %}

# when working_dir is set, assume that is the base and remove the rest
{% if working_dir %}
    mv {{working_dir}} /opt && rm -rf /opt/{{basename}}
    cd /opt/{{working_dir}}

    {% set basedir = working_dir %}
{% endif %}

# brutally remove virtualenv stuff from the current directory
rm -rf bin include lib local

virtualenv -p $CUSTOM_PYTHON_PATH/bin/python .

source bin/activate

if [ -f "$PWD{{requirements_path}}" ]; then
    pip install -r $PWD{{requirements_path}}
fi

if [ -f "setup.py" ]; then
    python setup.py install
fi

cd /

# get rid of VCS info
find /opt -type d -name '.git' -print0 | xargs -0 rm -rf
find /opt -type d -name '.svn' -print0 | xargs -0 rm -rf

fpm -s dir -t deb -n {{app}} -p /opt -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} /opt/{{basedir}} $CUSTOM_PYTHON_PATH

chown -R {{local_uid}}:{{local_gid}} /opt
