#!/bin/bash

# Usage: to be executed as
# docker cp validate-on-openstack.sh openstack:/
# docker exec -it openstack /validate-on-openstack.sh

set -x
set -e

source /openrc
openstack network list

# A handle for all objects in this session
UUID=$(cat /proc/sys/kernel/random/uuid)

# Create a new project/network in default domain
PROJ=p1-${UUID}
openstack project create ${PROJ}
openstack role add --user admin --project ${PROJ} user
openstack --os-project-name ${PROJ} network list
openstack --os-project-name ${PROJ} network create p1n1-${UUID}

# Create a new domain/project/network
DOMAIN=d1-${UUID}
openstack domain create ${DOMAIN}
openstack project create --domain ${DOMAIN} d1p1-${UUID}
# neutron needs to be used since openstack can't seem to work with new domain
PROJECT_ID=$(openstack project show d1p1-${UUID} | grep " id " | awk '{ print $4 }')
neutron net-create d1p1n1-${UUID} --tenant-id ${PROJECT_ID}
