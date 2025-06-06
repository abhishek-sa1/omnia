OIM logs
----------

.. caution:: It is not recommended to delete the below log files or the directories they reside in.

.. note::
    * Log files are rotated periodically as a storage consideration. To customize how often logs are rotated, edit the ``/etc/logrotate.conf`` file on the node.
    * If you want log files for specific playbook execution, ensure to use the ``cd`` command to move into the specific directory before executing the playbook. For example, if you want local repo logs, ensure to enter ``cd local_repo`` before executing the playbook. If the directory is not changed, all the playbook execution log files will be consolidated and provided as part of omnia logs located in ``/var/log/omnia.log``.

Loki logs
----------

Almost all log files can be viewed using the Dashboard tab ( |Dashboard| ) on the Grafana UI. Below is a list of all logs available to Loki and can be accessed from the dashboard:

.. csv-table:: Loki log files
   :file: ../Tables/ControlPlaneLogs.csv
   :header-rows: 1
   :keepspace:

.. image:: ../images/Grafana_Loki_TG.png

Logs of individual containers
-------------------------------
   1. A list of namespaces and their corresponding pods can be obtained using:
      ``kubectl get pods -A``
   2. Get a list of containers for the pod in question using:
      ``kubectl get pods <pod_name> -o jsonpath='{.spec.containers[*].name}'``
   3. Once you have the namespace, pod and container names, run the below command to get the required logs:
      ``kubectl logs pod <pod_name> -n <namespace> -c <container_name>``

Provisioning logs
--------------------

Logs pertaining to actions taken during ``discovery_provision.yml``  can be viewed in ``/var/log/xcat/cluster.log`` and ``/var/log/xcat/computes.log`` on the OIM.

.. note::  As long as a node has been added to a cluster by Omnia, deployment events taking place on the node will be updated in ``/var/log/xcat/cluster.log``.


Telemetry logs
---------------

Logs pertaining to actions taken by Omnia or iDRAC telemetry can be viewed in ``/var/log/messages``. Each log entry is tagged "omnia_telemetry". Log entries typically follow this format. ::

    <Date time> <Node name> omnia_telemetry[<Process ID>]: <name of file>:<name of method throwing error>: <Error message>


Grafana Loki
--------------

After `telemetry.yml <../Telemetry/index.html>`_ is run, Grafana services are installed on the OIM.

    i. Get the Grafana IP using ``kubectl get svc -n grafana``.

    ii. Login to the Grafana UI by connecting to the cluster IP of grafana service via port 5000. That is ``http://xx.xx.xx.xx:5000/login``.

    iii. In the Explore page, select **oim-node-loki**.

        .. image:: ../images/oim_grafana_loki.png

    iv. The log browser allows users to filter logs by job, node, user, etc.
        Example ::

            (job= "cluster deployment logs") |= "nodename"
            (job="compute log messages") |= "nodename" |="node_username"

Custom dashboards can be created as per your requirement.

.. |Dashboard| image:: ../images/Visualization/DashBoardIcon.png
    :height: 25px
