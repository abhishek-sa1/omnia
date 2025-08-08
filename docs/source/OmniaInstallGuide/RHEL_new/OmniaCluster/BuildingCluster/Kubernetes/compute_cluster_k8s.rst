==========================================
Set up Kubernetes on the compute cluster
==========================================

Prerequisites
===============

* Ensure that ``k8s`` entry is present in the ``softwares`` list in ``software_config.json``, as mentioned below:
    
    ::

        "softwares": [
                        {"name": "k8s", "version":"1.31.4"},
                     ]

* Ensure to run ``local_repo.yml`` with the ``k8s`` entry present in ``software_config.json``, to download all required Kubernetes packages and images.

* Once all the required parameters in `omnia_config.yml <../schedulerinputparams.html#id12>`_ are filled in, ``omnia.yml`` can be used to set up Kubernetes.

* Ensure that ``k8s_share`` is set to ``true`` in `storage_config.yml <../schedulerinputparams.html#storage-config-yml>`_, for one of the entries in ``nfs_client_params``.

Inventory details
==================

* All the applicable inventory groups are ``kube_control_plane``, ``kube_node``, and ``etcd``.
* The inventory file must contain:

        1. Exactly 1 ``kube_control_plane``.
        2. At least 1 ``kube_node`` [Optional].
        3. Odd number of ``etcd`` nodes.

.. note:: Ensure that the inventory includes an ``[etcd]`` node. etcd is a consistent and highly-available key value store used as Kubernetes' backing store for all cluster data. For more information, `click here. <https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/>`_

Sample inventory
=================

    ::

        [kube_control_plane]

        10.5.1.101

        [kube_node]

        10.5.1.102

        [etcd]

        10.5.1.101


Playbook execution
===================

Run either of the following playbooks, where ``-i <inventory>`` denotes the file path of the user specified inventory:

    1. ::

            cd omnia
            ansible-playbook omnia.yml -i <inventory>

    2. ::

            cd scheduler
            ansible-playbook scheduler.yml -i <inventory>

Additional installations
=========================

.. note:: 
    
    * Additional packages for Kubernetes will be deployed only if ``nfs`` entry is present in the ``/opt/omnia/input/project_default/software_config.json``.
    * If the ``nfs_server_ip`` in ``/opt/omnia/input/project_default/storage_config.yml`` is left blank, you must provide a valid external NFS server IP for the ``nfs_server_ip`` parameter.

After deploying Kubernetes, you can install the following additional packages on top of the Kubernetes stack on the compute cluster:

1.	**amdgpu-device-plugin (ROCm device plugin)**

    This is a Kubernetes device plugin implementation that enables the registration of AMD GPU in a container cluster for compute workload.
    Click `here <https://github.com/ROCm/k8s-device-plugin>`_ for more information.

2.	**mpi-operator**

    The MPI Operator makes it easy to run allreduce-style distributed training on Kubernetes.
    Click `here <https://github.com/kubeflow/mpi-operator>`_ for more information.

3.	**xilinx device plugin*

    The Xilinx FPGA device plugin for Kubernetes is a Daemonset deployed on the Kubernetes (k8s) cluster which allows you to:

        i.	Discover the FPGAs inserted in each node of the cluster and expose information about FPGA such as number of FPGA, Shell (Target Platform) type and etc.

        ii.	Run FPGA accessible containers in the k8s cluster

    Click `here <https://github.com/Xilinx/FPGA_as_a_Service/tree/master/k8s-device-plugin>`_ for more information.

4. **nfs-client-provisioner**

        * NFS subdir external provisioner is an automatic provisioner that use your existing and already configured NFS server to support dynamic provisioning of Kubernetes Persistent Volumes via Persistent Volume Claims.
        * The NFS server utilised here is the one mentioned in ``storage_config.yml``.
        * Server IP is ``<nfs_client_params.server_ip>`` and path is ``<nfs_client_params>.<server_share_path>`` of the entry where ``k8s_share`` is set to ``true``.

    Click `here <https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner>`_ for more information.

5.	**nvidia-device-plugin**

    For the NVIDIA device plugin to function seamlessly, Omnia installs the "nvidia-container-toolkit" as part of the ``omnia.yml`` or ``scheduler.yml`` playbook execution. The NVIDIA device plugin for Kubernetes is a "DaemonSet" that allows you to automatically:

        i.	Expose the number of GPUs on each nodes of your cluster
        ii.	Keep track of the health of your GPUs
        iii. Run GPU enabled containers in your Kubernetes cluster

    Click `here <https://github.com/NVIDIA/k8s-device-plugin>`_ for more information.

6. **nvidia-gpu-operator**

    The NVIDIA GPU Operator uses the operator framework within Kubernetes to automate the management of all software components needed to provision NVIDIA GPUs.
    These components include the NVIDIA drivers (to enable CUDA), Kubernetes device plugin for GPUs, the NVIDIA Container Toolkit, automatic node labelling using GFD, DCGM based monitoring and others.
    Omnia installs the NVIDIA GPU operator as part of ``omnia.yml`` playbook execution.

    For more information on how to configure the NVIDIA GPU operator with Omnia, `click here <nvidia_gpu_operator.html>`_.

7.  **gaudi-device-plugin**

    The Gaudi device plugin is a Kubernetes device plugin implementation that enables the registration of Intel Gaudi AI accelerators in a container cluster. This plugin enables the efficient utilization of Gaudi accelerators for compute workloads within the cluster.
    For the gaudi-device-plugin to function seamlessly, Omnia installs the “habanalabs-container-runtime” as part of the ``omnia.yml`` or ``scheduler.yml`` playbook execution.

    The Gaudi device plugin for Kubernetes is a “DaemonSet” that allows you to automatically:

        i. Enable the registration of Intel Gaudi accelerators in your Kubernetes cluster.
        ii. Keep track of device health.
        iii. Run jobs on the Intel Gaudi accelerators.

    Click `here <https://docs.habana.ai/en/latest/Orchestration/Gaudi_Kubernetes/Device_Plugin_for_Kubernetes.html>`_ for more information.

8. **whereabouts-cni-plugin**

    Whereabouts is an IP address management (IPAM) CNI plugin that assigns dynamic IP addresses cluster-wide in Kubernetes, ensuring no IP address collisions across nodes.
    It uses a range of IPs and tracks assignments with backends like etcd or Kubernetes Custom Resources.
    Omnia installs the whereabouts plugin as part of ``omnia.yml`` or ``scheduler.yml`` execution. The details of the plugin is present in the ``omnia/input/config/<cluster os>/<os version>/k8s.json`` file.

    Click `here <https://github.com/k8snetworkplumbingwg/whereabouts>`_ for more information.

9. **multus-cni-plugin**

    Multus is a Kubernetes CNI (Container Network Interface) plugin that enables pods to have multiple network interfaces. It acts as a meta-plugin, allowing the use of multiple CNI plugins (for example, Flannel, Calico, Macvlan) within the same cluster.
    Omnia installs the multus plugin as part of ``omnia.yml`` or ``scheduler.yml`` execution. The details of the plugin is present in the ``omnia/input/config/<cluster os>/<os version>/k8s.json`` file.

    Click `here <https://github.com/k8snetworkplumbingwg/multus-cni>`_ for more information.

10. **CSI-driver-for-PowerScale**

    The CSI Driver for Dell PowerScale (formerly known as Isilon) is a Container Storage Interface (CSI) plugin that enables Kubernetes to provision and manage persistent storage using PowerScale.
    It enables Kubernetes clusters to dynamically provision, bind, expand, snapshot, and manage volumes on a PowerScale node.
    Omnia installs the multus plugin as part of ``omnia.yml`` or ``scheduler.yml`` execution.

    Click `here <../../../../AdvancedConfigurations/PowerScale_CSI.html>`_ for more information.