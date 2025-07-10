Soft reset the cluster
=======================

Use this playbook to stop and remove all Slurm and Kubernetes services from the cluster nodes.

.. warning:: This action will destroy the existing Slurm/Kubernetes cluster.

.. note::
    * All target nodes should be drained before executing the playbook. If a job is running on any target nodes, the playbook may timeout while waiting for the node state to change.
    * When running ``reset_cluster_configuration.yml``, ensure that the ``input/storage_config.yml`` and ``input/omnia_config.yml`` have not been edited since ``omnia.yml`` was run.

**Configurations performed by the playbook**

    * The Slurm and Kubernetes configuration will be reset on the ``kube_control_plane`` or the ``slurm_control_node``, as defined in the inventory file.
    * All services related to Slurm and Kubernetes are stopped and removed.

**To run the playbook**

Run the playbook using the following commands: ::

        cd utils
        ansible-playbook reset_cluster_configuration.yml -i inventory

* To specify only Slurm or Kubernetes clusters while running the playbook, use the tags ``slurm_cluster`` or ``k8s_cluster``. That is:

    * To reset a slurm cluster, use ``ansible-playbook reset_cluster_configuration.yml -i inventory --tags slurm_cluster``.
    * To reset a kubernetes cluster, use ``ansible-playbook reset_cluster_configuration.yml -i inventory --tags k8s_cluster``.

.. caution:: If you do not specify the tags ``slurm_cluster`` or ``k8s_cluster``, the ``reset_cluster_configuration.yml`` will reset the configuration for both Slurm and Kubernetes clusters.

* To skip confirmation while running the playbook, use ``ansible-playbook reset_cluster_configuration.yml -i inventory --extra-vars skip_confirmation=yes`` or ``ansible-playbook reset_cluster_configuration.yml -i inventory -e  skip_confirmation=yes``.

The inventory file passed for ``reset_cluster_configuration.yml`` should follow the below format. ::

        #Batch Scheduler: Slurm

        [slurm_control_node]

        10.5.1.101

        [slurm_node]

        10.5.1.103

        10.5.1.104

        [login]

        10.5.1.105


        #General Cluster Storage

        [auth_server]

        10.5.1.106


        #AI Scheduler: Kubernetes

        [kube_control_plane]

        10.5.1.101

        [etcd]

        10.5.1.101

        [kube_node]

        10.5.1.102

        10.5.1.103

        10.5.1.104

        10.5.1.105

        10.5.1.106

.. note:: After running the ``reset_cluster_configuration.yml`` playbook on a Kubernetes cluster, it is observed that some Kubernetes logs and configuration files are still present on the ``kube_control_plane``. For more information about this, `click here <../../Troubleshooting/KnownIssues/Common/Kubernetes.html>`_.