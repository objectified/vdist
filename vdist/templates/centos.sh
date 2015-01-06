#!/bin/bash -x

# install fpm
yum check-update 
yum install -y ruby-devel gcc curl libyaml-devel which tar rpm-build rubygems

gem install fpm

# install prerequisites
yum install -y git python-setuptools
easy_install virtualenv

# install build dependencies
yum install -y {{build_deps|join(' ')}}

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

fpm -s dir -t rpm -n {{app}} -p /dist -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} {{app}}
