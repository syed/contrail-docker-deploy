#!/bin/bash

crudini --set /etc/neutron/neutron.conf keystone_authtoken auth_uri http://openstack:35357/v2.0/
crudini --set /etc/neutron/neutron.conf keystone_authtoken identity_uri http://openstack:5000
crudini --set /etc/neutron/neutron.conf keystone_authtoken admin_tenant_name admin
crudini --set /etc/neutron/neutron.conf keystone_authtoken admin_user neutron
crudini --set /etc/neutron/neutron.conf keystone_authtoken admin_password ${NEUTRON_PASS}

crudini --set /etc/neutron/neutron.conf DEFAULT verbose True
crudini --set /etc/neutron/neutron.conf DEFAULT debug True

/usr/bin/neutron-server
