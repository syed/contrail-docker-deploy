#!/bin/bash
set -x

touch /etc/contrail/contrail-discovery.conf
if [ "$CASSANDRA_SERVERS" ]; then
    crudini --set /etc/contrail/contrail-discovery.conf DEFAULTS cassandra_server_list ${CASSANDRA_SERVERS}
fi

/usr/bin/contrail-discovery --conf_file /etc/contrail/contrail-discovery.conf
