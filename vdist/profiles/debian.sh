#!/bin/bash -x
PYTHON_VERSION="{{compile_python_version}}"
PYTHON_BASEDIR="{{python_basedir}}"

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

{% if compile_python %}
    apt-get build-dep python -y
    apt-get install libssl-dev -y

    # compile and install python
    cd /var/tmp
    curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
    tar xzvf Python-$PYTHON_VERSION.tgz
    cd Python-$PYTHON_VERSION
    ./configure --prefix=$PYTHON_BASEDIR
    make && make install

{% endif %}

cd {{package_build_root}}

{% if source.type == 'git' %}

    git clone {{source.uri}}
    cd {{basename}}
    git checkout {{source.branch}}

{% elif source.type in ['directory', 'git_directory'] %}

    cp -r {{shared_dir}}/{{scratch_dir}}/{{basename}} .
    cd {{package_build_root}}/{{basename}}

    {% if source.type == 'git_directory' %}
        git checkout {{source.branch}}
    {% endif %}

{% else %}

    echo "invalid source type, exiting."
    exit 1


{% endif %}

{% if use_local_pip_conf %}
    cp -r /work/scratch/.pip ~
{% endif %}

# when working_dir is set, assume that is the base and remove the rest
{% if working_dir %}
    mv {{working_dir}} {{package_build_root}} && rm -rf {{package_build_root}}/{{basename}}
    cd {{package_build_root}}/{{working_dir}}

    {% set basedir = working_dir %}
{% endif %}

# brutally remove virtualenv stuff from the current directory
rm -rf bin include lib local

virtualenv -p $PYTHON_BASEDIR/bin/python .

source bin/activate

if [ -f "$PWD{{requirements_path}}" ]; then
    pip install {{pip_args}} -r $PWD{{requirements_path}}
fi

if [ -f "setup.py" ]; then
    python setup.py install
fi

cd /

# get rid of VCS info
find {{package_build_root}} -type d -name '.git' -print0 | xargs -0 rm -rf
find {{package_build_root}} -type d -name '.svn' -print0 | xargs -0 rm -rf

fpm -s dir -t deb -n {{app}} -p {{package_build_root}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} {{package_build_root}}/{{basedir}} $PYTHON_BASEDIR

cp {{package_build_root}}/*deb {{shared_dir}}

chown -R {{local_uid}}:{{local_gid}} {{shared_dir}}
