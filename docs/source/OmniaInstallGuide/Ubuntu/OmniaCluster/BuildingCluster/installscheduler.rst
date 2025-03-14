Cluster formation
====================

1. In the ``input/omnia_config.yml``, ``input/security_config.yml``, and ``input/storage_config.yml`` files, provide the `required details <../schedulerinputparams.html>`_. For ``input/telemetry_config.yml``, the details can be found `here <../../../../Telemetry/index.html#id13>`_.

2. Create an inventory file in the *omnia* folder. Check out the `sample inventory <../../../samplefiles.html>`_ for more information. If a hostname is used to refer to the target nodes, ensure that the domain name is included in the entry. IP addresses are also accepted in the inventory file.

.. include:: ../../Appendices/hostnamereqs.rst

.. note:: Omnia creates a log file which is available at: ``/var/log/omnia.log``.

3. ``omnia.yml`` is a wrapper playbook and achieves the following tasks:

    i. ``security.yml``: This playbook sets up centralized authentication (OpenLDAP) on the cluster. For more information, `click here. <Authentication.html>`_
    ii. ``storage.yml``: This playbook sets up storage tools such as, `NFS <Storage/NFS.html>`_.
    iii. ``scheduler.yml``: This playbook sets up the (`Kubernetes <install_kubernetes.html>`_) job scheduler on the cluster.
    iv. ``telemetry.yml``: This playbook sets up `Omnia telemetry and/or iDRAC telemetry <../../../../Telemetry/index.html>`_. It also installs `Grafana <https://grafana.com/>`_ and `Loki <https://grafana.com/oss/loki/>`_ as Kubernetes pods.
    v. ``rocm_installation.yml``: This playbook sets up the `ROCm platform for AMD GPU accelerators <AMD_ROCm.html>`_.
    vi. ``performance_profile.yml``: This playbook is located in the ``utils/performance_profile`` directory and it enables you to optimize system performance for specific workloads. For more information, see `Performance profile configuration <../../../../Utils/tuneD.html>`_.

.. note:: To run the ``scheduler.yml``, ``security.yml``, ``telemetry.yml``, or ``storage.yml`` playbook independently from the ``omnia.yml`` playbook on Intel Gaudi nodes, start by executing the ``performance_profile.yml`` playbook. Once that’s done, you can run the respective playbooks separately.

To run ``omnia.yml``: ::

        ansible-playbook omnia.yml -i inventory

.. note::
    * If you want to view or edit the ``omnia_config.yml`` file, run the following command:

                - ``ansible-vault view omnia_config.yml --vault-password-file .omnia_vault_key`` -- To view the file.

                - ``ansible-vault edit omnia_config.yml --vault-password-file .omnia_vault_key`` -- To edit the file.

    * Use the ansible-vault view or edit commands and not the ansible-vault decrypt or encrypt commands. If you have used the ansible-vault decrypt or encrypt commands, provide 644 permission to the parameter files.

4. Once ``omnia.yml`` playbook is successfully executed, the cluster is up and running with the required application stack. Now, you can install `AI tools <../../InstallAITools/index.html>`_ or utilize the cluster for job execution.

