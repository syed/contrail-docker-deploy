=======================
Contrail Docker Deploy
=======================

This repository is for containerization of OpenContrail. It is forked from Ajay Hampapur. It separates microservices into Docker containers, but also provides single container deployment for playground.

Simple Contrail Docker
==========================

This procedure deploys OpenStack and OpenContrail controllers in two Docker containers. This is very usefull for quick deploy and testing. It is still under developement and testing. It supports now OpenContrail 3.0 and OpenStack Kilo controllers. Compute node and vRouter is in progress.

First clone following repositories:

.. code-block:: bash

	$ git clone https://github.com/pupapaik/contrail-docker-deploy.git
	$ git clone https://github.com/pupapaik/openstack-controller-docker.git

Move into directory

.. code-block:: bash

	$ cd contrail-docker-deploy/modes/simple-contrail-docker/

Run docker compose

.. code-block:: bash

	$ docker-compose -f compose.yml up -d

	Creating simplecontraildocker_contrail_1
	Creating simplecontraildocker_openstack_1

It launch two containers:

.. code-block:: bash

	$ docker ps
	CONTAINER ID        IMAGE                             COMMAND                  CREATED             STATUS              PORTS                                        NAMES
	00a946e9103d        simplecontraildocker_openstack    "/entrypoint.sh"         2 seconds ago       Up 2 seconds                                                     simplecontraildocker_openstack_1
	c982fc736e64        simplecontraildocker_contrail     "/bin/sh -c '/usr/bin"   2 seconds ago       Up 2 seconds        0.0.0.0:80->80/tcp, 0.0.0.0:8143->8143/tcp   simplecontraildocker_contrail_1

Now your OpenStack and OpenContrail controllers are ready :) . You can inspire in validate-on-openstack.sh for basic testing or open browser http://localhost/horizon and https://localhost:8143 . Compute node side has not finished yet. Contribution is welcome :)