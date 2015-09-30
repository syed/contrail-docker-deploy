FROM ubuntu:14.04.3
MAINTAINER Pedro Marques <roque@juniper.net>
RUN apt-get update
RUN apt-get install -y software-properties-common curl patch
RUN add-apt-repository cloud-archive:kilo
RUN apt-add-repository -y ppa:opencontrail
RUN apt-add-repository -y ppa:opencontrail/r2.20
RUN apt-get update
RUN echo exit 101 > /usr/sbin/policy-rc.d
RUN chmod +x /usr/sbin/policy-rc.d
RUN apt-get install -y neutron-server
#RUN apt-get install -y python-neutron-lbaas
RUN apt-get install -y neutron-plugin-contrail
RUN apt-get install -y crudini

RUN crudini --set /etc/neutron/neutron.conf DEFAULT log_file /var/log/neutron/server.log
RUN crudini --set /etc/neutron/neutron.conf DEFAULT core_plugin neutron_plugin_contrail.plugins.opencontrail.contrail_plugin.NeutronPluginContrailCoreV2
RUN crudini --set /etc/neutron/neutron.conf DEFAULT api_extensions_path extensions:/usr/lib/python2.7/dist-packages/neutron_plugin_contrail/extensions
RUN crudini --set /etc/neutron/neutron.conf quotas quota_driver neutron_plugin_contrail.plugins.opencontrail.quota.driver.QuotaDriver
#RUN crudini --set /etc/neutron/neutron.conf DEFAULT service_plugins neutron_plugin_contrail.plugins.opencontrail.loadbalancer.plugin.LoadBalancerPlugin
#RUN crudini --set /etc/neutron/neutron.conf service_providers service_provider LOADBALANCER:Opencontrail:neutron_plugin_contrail.plugins.opencontrail.loadbalancer.driver.OpencontrailLoadbalancerDriver:default

COPY entrypoint.sh /entrypoint.sh

CMD ["/entrypoint.sh"]
