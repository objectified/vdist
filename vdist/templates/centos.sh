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

cd /build

git clone {{git_url}}

cd {{app}}

virtualenv .

source bin/activate

pip install -r requirements.txt

cd ..

fpm -s dir -t rpm -n {{app}} -p /build -v {{version}} {% for dep in runtime_deps %} --depends {{dep}} {% endfor %} {{fpm_args}} {{app}}
