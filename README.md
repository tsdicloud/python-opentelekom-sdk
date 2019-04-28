### Prepare for development/functional testing

. Install required libraries
$ sudo /usr/local/bin/pip3 install -r openstacksdk/test_requirements.txt
$ sudo /usr/local/bin/pip3 tox

. Prepare a cloud.yml for your cloud

. Run functional tests
$ cd opentelekom/tests
$ export PBR_VERSION=0.8.0
$ tox -e functional3 