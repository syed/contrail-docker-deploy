FROM ubuntu:14.04
MAINTAINER Pedro Marques <roque@juniper.net>
RUN apt-get update
RUN apt-get install -y software-properties-common curl patch
RUN add-apt-repository cloud-archive:kilo
RUN apt-add-repository -y ppa:opencontrail
RUN apt-add-repository -y ppa:opencontrail/r2.20
RUN apt-get update
RUN apt-get install -y crudini
RUN apt-get install -y contrail-config-openstack
RUN apt-get download contrail-config
RUN apt-get install -y $(apt-cache depends contrail-config | egrep -v "supervisor|<.*>" | grep Depends | sed "s/.*ends:\ //" | tr '\n' ' ')
RUN dpkg --unpack contrail-config*.deb
RUN rm -f /var/lib/dpkg/info/contrail-config.postinst


RUN sed -i 's/parser.add_argument("--disc_server_ip", help="IP address of discovery server")//' /usr/lib/python2.7/dist-packages/vnc_cfg_api_server/utils.py

# TMP Apply ifmap client.py patch https://review.opencontrail.org/#/c/12816/2
RUN sed -i 's/ : PROTOCOL_SSLv23/ : PROTOCOL_TLSv1/' /usr/lib/python2.7/dist-packages/cfgm_common/ifmap/client.py
RUN sed -i 's/sys.version_info/False and sys.version_info/' /usr/lib/python2.7/dist-packages/cfgm_common/ifmap/client.py

# TMP Fix discovery server startup issue
RUN sed -i 's/\(.*update.*DEFAULTS.*\)/#\ \1/' /usr/lib/python2.7/dist-packages/discovery/disc_server.py

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT /entrypoint.sh
