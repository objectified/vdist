#!/bin/bash -x
PYTHON_VERSION="2.7.9"

# fail on error
set -e

# install general prerequisites
yum -y update
yum install -y ruby-devel curl libyaml-devel which tar rpm-build rubygems git python-setuptools zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel

yum groupinstall -y "Development Tools"

# install build dependencies needed for this specific build
{% if build_deps %}
yum install -y {{build_deps|join(' ')}}
{% endif %}

# only install when needed, to save time with
# pre-provisioned containers
if [ ! -f /usr/bin/fpm ]; then
    gem install fpm
fi

# install prerequisites
easy_install virtualenv

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
    cd {{basename}}
    git checkout {{source.branch}}
    rm -rf .git

{% elif source.type == 'directory' %}

    cp -r /opt/scratch/{{basename}} .
    cd /opt/{{basename}}

{% else %}

    echo "invalid source type, exiting."
    exit 1

{% endif %}


{% if use_local_pip_conf %}
    cp -r /opt/scratch/.pip ~
{% endif %}

{% if working_dir %}
    cd {{working_dir}}
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

fpm -s dir -t rpm -n {{app}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} /opt

chown -R {{local_uid}}:{{local_gid}} /opt
