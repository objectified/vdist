#!/bin/bash -x
PYTHON_VERSION="{{python_version}}"
PYTHON_BASEDIR="{{python_basedir}}"

# fail on error
set -e

# install fpm
apt-get update
apt-get install ruby-dev build-essential git python-virtualenv curl libssl-dev libsqlite3-dev libgdbm-dev libreadline-dev libbz2-dev libncurses5-dev tk-dev python3 python3-pip -y

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
    ./configure --prefix=$PYTHON_BASEDIR --with-ensurepip=install
    make && make install
{% endif %}

if [ ! -d {{package_tmp_root}} ]; then
    mkdir -p {{package_tmp_root}}
fi

cd {{package_tmp_root}}

{% if source.type == 'git' %}

    git clone {{source.uri}}
    cd {{project_root}}
    git checkout {{source.branch}}

{% elif source.type in ['directory', 'git_directory'] %}

    cp -r {{scratch_dir}}/{{project_root}} .
    cd {{package_tmp_root}}/{{project_root}}

    {% if source.type == 'git_directory' %}
        git checkout {{source.branch}}
    {% endif %}

{% else %}

    echo "invalid source type, exiting."
    exit 1


{% endif %}

{% if use_local_pip_conf %}
    cp -r {{scratch_dir}}/.pip ~
{% endif %}

# when working_dir is set, assume that is the base and remove the rest
{% if working_dir %}
    mv {{working_dir}} {{package_tmp_root}} && rm -rf {{package_tmp_root}}/{{project_root}}
    cd {{package_tmp_root}}/{{working_dir}}

    # reset project_root
    {% set project_root = working_dir %}
{% endif %}

# brutally remove virtualenv stuff from the current directory
rm -rf bin include lib local

if [[ ${PYTHON_VERSION:0:1} == "2" ]]; then
    PYTHON_BIN="$PYTHON_BASEDIR/bin/python"
    PIP_BIN="$PYTHON_BASEDIR/bin/pip"
else
    PYTHON_BIN="$PYTHON_BASEDIR/bin/python3"
    PIP_BIN="$PYTHON_BASEDIR/bin/pip3"
fi

if [ -f "$PWD{{requirements_path}}" ]; then
    $PIP_BIN install -U pip setuptools
    virtualenv -p $PYTHON_BIN .
    source bin/activate
    $PIP_BIN install {{pip_args}} -r $PWD{{requirements_path}}
fi

if [ -f "setup.py" ]; then
    $PYTHON_BIN setup.py install
    built=true
else
    built=false
fi

cd /

# get rid of VCS info
find {{package_tmp_root}} -type d -name '.git' -print0 | xargs -0 rm -rf
find {{package_tmp_root}} -type d -name '.svn' -print0 | xargs -0 rm -rf

if $built; then
    {% if custom_filename %}
        fpm -s dir -t deb -n {{app}} -p {{package_tmp_root}}/{{custom_filename}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} $PYTHON_BASEDIR
    {% else %}
        fpm -s dir -t deb -n {{app}} -p {{package_tmp_root}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} $PYTHON_BASEDIR
    {% endif %}
    cp {{package_tmp_root}}/*deb {{shared_dir}}
else
    mkdir -p {{package_install_root}}/{{app}}
    cp -r {{package_tmp_root}}/{{app}}/* {{package_install_root}}/{{app}}/.
    {% if custom_filename %}
        fpm -s dir -t deb -n {{app}} -p {{package_tmp_root}}/{{custom_filename}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} {{package_install_root}}/{{project_root}} $PYTHON_BASEDIR
    {% else %}
        fpm -s dir -t deb -n {{app}} -p {{package_tmp_root}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} {{package_install_root}}/{{project_root}} $PYTHON_BASEDIR
    {% endif %}
    cp {{package_tmp_root}}/*deb {{shared_dir}}
fi

chown -R {{local_uid}}:{{local_gid}} {{shared_dir}}
