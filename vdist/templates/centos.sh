#!/bin/bash -x

# install fpm
yum check-update 
yum install -y ruby-devel gcc curl libyaml-devel which tar rpm-build

gpg --keyserver hkp://keys.gnupg.net --recv-keys D39DC0E3

curl -sSL get.rvm.io | bash -s stable
source /etc/profile.d/rvm.sh

rvm requirements
rvm install 1.9.3
rvm use 1.9.3 --default

rvm rubygems current

gem install fpm

# install prerequisites
yum install -y git python-setuptools
easy_install virtualenv

# install build dependencies
yum install -y {{build_deps|join(' ')}}

cd /opt

git clone {{git_url}}

cd {{app}}

virtualenv .

source bin/activate

pip install -r requirements.txt

cd ..

fpm -s dir -t rpm -n {{app}} {{app}}
