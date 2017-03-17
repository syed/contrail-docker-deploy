#!/bin/bash

sudo apt-get install -y \
        linux-image-extra-$(uname -r) \
        linux-image-extra-virtual


sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        software-properties-common

curl https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"


sudo apt-get update

sudo apt-get install -y docker-ce

curl -L https://github.com/docker/compose/releases/download/1.11.2/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

