Remove Slurm/Kubernetes configuration from a compute node
================================================================

Use this playbook to remove the Slurm and/or Kubernetes configuration and stop all clustering software on the compute nodes of the cluster. This will help to clean up the cluster and ensure that all clustering components are properly deactivated and removed from the compute nodes.

.. note::
    * All target nodes should be drained before executing the playbook. If a job is running on any target nodes, the playbook may timeout waiting for the node state to change.
    * When running ``remove_node_configuration.yml``, ensure that the ``input/storage_config.yml`` and ``input/omnia_config.yml`` have not been edited since the last run of ``omnia.yml``.

.. caution:: While attempting to remove a slurm_node configured on a cluster, the ``slurmctld`` services might fail on the ``slurm_control_node``. This happens only when there is a single ``slurm_node`` present in the cluster.

**Configurations performed by the playbook**

    * Nodes specified in the ``slurm_node`` or ``kube_node`` group in the inventory file will be removed from the Slurm or Kubernetes cluster respectively.
    * Slurm and Kubernetes services are stopped and uninstalled. OS startup service list will be updated to disable Slurm and Kubernetes.

**To run the playbook**

* Insert the IP of the compute node(s) to be removed, in the existing inventory file as shown below:

*Existing Kubernetes inventory*
::
    [kube_control_plane]
    10.5.0.101

    [kube_node]
    10.5.0.102
    10.5.0.103
    10.5.0.105
    10.5.0.106

    [auth_server]
    10.5.0.101

    [etcd]
    10.5.0.110

*New inventory for removing Kube nodes from the cluster*
::

    [kube_node]
    10.5.0.102
    10.5.0.103

*Existing Slurm inventory*
::
    [slurm_control_node]
    10.5.0.101

    [slurm_node]
    10.5.0.102
    10.5.0.103
    10.5.0.105
    10.5.0.106

    [login]
    10.5.0.104

    [auth_server]
    10.5.0.101

*New inventory for removing Slurm nodes from the cluster*
::
    [slurm_node]
    10.5.0.102
    10.5.0.103

* To run the playbook, run the following commands: ::

       cd utils
       ansible-playbook remove_node_configuration.yml -i inventory

* To specify only Slurm or Kubernetes nodes while running the playbook, use the tags ``slurm_node`` or ``kube_node``. That is:

    * To remove only Slurm nodes, use ``ansible-playbook remove_node_configuration.yml -i inventory --tags slurm_node``.
    * To remove only Kubernetes nodes, use ``ansible-playbook remove_node_configuration.yml -i inventory --tags kube_node``.

* To skip confirmation while running the playbook, use ``ansible-playbook remove_node_configuration.yml -i inventory --extra-vars skip_confirmation=yes`` or ``ansible-playbook remove_node_configuration.yml -i inventory -e  skip_confirmation=yes``.