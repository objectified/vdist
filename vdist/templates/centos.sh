#!/bin/bash -x
PYTHON_VERSION="2.7.9"

# install general prerequisites
yum check-update 
yum install -y ruby-devel curl libyaml-devel which tar rpm-build rubygems git python-setuptools zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel

yum groupinstall -y "Development Tools"

# install build dependencies needed for this specific build
{% if build_deps %}
yum install -y {{build_deps|join(' ')}}
{% endif %}

gem install fpm

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

fpm -s dir -t rpm -n {{app}} -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} /opt
