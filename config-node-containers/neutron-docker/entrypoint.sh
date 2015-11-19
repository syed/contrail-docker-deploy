#!/bin/bash

KEYSTONE_HOST=${KEYSTONE_HOST:-openstack}
NEUTRON_TENANT_NAME=${NEUTRON_TENANT_NAME:-admin}
NEUTRON_USER=${NEUTRON_TENANT_NAME:-admin}
CONTRAIL_API_HOST=${CONTRAIL_API_HOST:-localhost}

crudini --set /etc/neutron/neutron.conf keystone_authtoken auth_uri http://${KEYSTONE_HOST}:35357/v2.0/
crudini --set /etc/neutron/neutron.conf keystone_authtoken identity_uri http://${KEYSTONE_HOST}:5000
crudini --set /etc/neutron/neutron.conf keystone_authtoken admin_tenant_name ${NEUTRON_TENANT_NAME}
crudini --set /etc/neutron/neutron.conf keystone_authtoken admin_user ${NEUTRON_USER}
crudini --set /etc/neutron/neutron.conf keystone_authtoken admin_password ${NEUTRON_PASS}

crudini --set /etc/neutron/neutron.conf APISERVER api_server_ip ${CONTRAIL_API_HOST}
crudini --set /etc/neutron/neutron.conf APISERVER contrail_extensions ipam:neutron_plugin_contrail.plugins.opencontrail.contrail_plugin_ipam.NeutronPluginContrailIpam,policy:neutron_plugin_contrail.plugins.opencontrail.contrail_plugin_policy.NeutronPluginContrailPolicy,route-table:neutron_plugin_contrail.plugins.opencontrail.contrail_plugin_vpc.NeutronPluginContrailVpc

crudini --set /etc/neutron/neutron.conf DEFAULT verbose True
crudini --set /etc/neutron/neutron.conf DEFAULT debug True

/usr/bin/neutron-server
