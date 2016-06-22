#!/bin/bash -x
PYTHON_VERSION="{{python_version}}"
PYTHON_BASEDIR="{{python_basedir}}"
CONTAINER_PYTHON3_VERSION="5"

# fail on error
set -e

# install general prerequisites
yum -y update
yum groupinstall -y "Development Tools"
yum install -y ruby-devel curl libyaml-devel which tar rpm-build rubygems git python-setuptools zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel gcc gcc-c++
yum install -y yum-utils

# Python 3 RPM installation to get basic support in that Python version.
# Idea taken from: http://stackoverflow.com/questions/8087184/problems-installing-python3-on-rhel
yum install -y https://centos6.iuscommunity.org/ius-release.rpm
yum install -y python3${CONTAINER_PYTHON3_VERSION}u python3${CONTAINER_PYTHON3_VERSION}u-pip
ln -s /usr/bin/python3.$CONTAINER_PYTHON3_VERSION /usr/bin/python3
ln -s /usr/bin/pip3.$CONTAINER_PYTHON3_VERSION /usr/bin/pip3

# install build dependencies needed for this specific build
{% if build_deps %}
yum install -y {{build_deps|join(' ')}}
{% endif %}

# only install when needed, to save time with
# pre-provisioned containers
if [ ! -f /usr/bin/fpm ]; then
    # Latest ruby 1.5.0 fails to install in centos 6.
    # For more info read: https://github.com/jordansissel/fpm/issues/1090
    # So force to 1.4.0 needed.
    gem install fpm --version 1.4.0
fi

# install prerequisites
easy_install virtualenv

{% if compile_python %}
    # compile and install python
    cd /var/tmp
    curl -O https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz
    tar xzvf Python-$PYTHON_VERSION.tgz
    cd Python-$PYTHON_VERSION
    # Configure fails if folder in rpath doesn't exists before.
    # Creating it, even empty, before configure seems to solve issue.
    # More info in:
    #   http://koansys.com/tech/building-python-with-enable-shared-in-non-standard-location
    mkdir -p ${PYTHON_BASEDIR}/lib
    ./configure --prefix=$PYTHON_BASEDIR --enable-shared LDFLAGS="-Wl,-rpath ${PYTHON_BASEDIR}/lib"
    make
    make altinstall
    PYTHON_MAIN_VERSION=${PYTHON_VERSION:0:3}
    if [[ ${PYTHON_VERSION:0:1} == "2" ]]; then
        ln -s $PYTHON_BASEDIR/bin/python$PYTHON_MAIN_VERSION $PYTHON_BASEDIR/bin/python
        # At this point pip does not exists yet so we're creating a dead link
        # but later we are going to install pip through ensurepip module
        # so this is going to be fixed.
        ln -s $PYTHON_BASEDIR/bin/pip$PYTHON_MAIN_VERSION $PYTHON_BASEDIR/bin/pip
    else
        ln -s $PYTHON_BASEDIR/bin/python$PYTHON_MAIN_VERSION $PYTHON_BASEDIR/bin/python3
        ln -s $PYTHON_BASEDIR/bin/pip$PYTHON_MAIN_VERSION $PYTHON_BASEDIR/bin/pip3
    fi
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
    $PYTHON_BIN -m ensurepip
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
        fpm -s dir -t rpm -n {{app}} -p {{package_tmp_root}}/{{custom_filename}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} $PYTHON_BASEDIR
    {% else %}
        fpm -s dir -t rpm -n {{app}} -p {{package_tmp_root}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} $PYTHON_BASEDIR
    {% endif %}
    cp {{package_tmp_root}}/*rpm {{shared_dir}}
else
    mkdir -p {{package_install_root}}/{{app}}
    cp -r {{package_tmp_root}}/{{app}}/* {{package_install_root}}/{{app}}/.
    {% if custom_filename %}
        fpm -s dir -t rpm -n {{app}} -p {{package_tmp_root}}/{{custom_filename}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} {{package_install_root}}/{{project_root}} $PYTHON_BASEDIR
    {% else %}
        fpm -s dir -t rpm -n {{app}} -p {{package_tmp_root}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} {{package_install_root}}/{{project_root}} $PYTHON_BASEDIR
    {% endif %}
    cp {{package_tmp_root}}/*rpm {{shared_dir}}
fi

chown -R {{local_uid}}:{{local_gid}} {{shared_dir}}
