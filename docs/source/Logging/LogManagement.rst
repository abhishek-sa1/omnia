Log management
----------------

Use ``/etc/logrotate.conf`` to customize how often logs are rotated. The default settings for ``logrotate.conf`` are: ::

    cat /etc/logrotate.conf
    # see "man logrotate" for details
    # rotate log files weekly
    weekly
    # keep 4 weeks worth of backlogs
    rotate 4
    # create new (empty) log files after rotating old ones
    create
    # use date as a suffix of the rotated file
    dateext
    # uncomment this if you want your log files compressed
    #compress
    # RPM packages drop log rotation information into this directory
    include /etc/logrotate.d
    # system-specific logs may be also be configured here.

With the above settings:

    * Logs are backed up weekly.

    * Data upto 4 weeks old is backed up. Any log backup older than four weeks will be deleted.

.. caution:: Since these logs take up ``/var`` space, sufficient space must be allocated to ``/var`` partition if it's created. If ``/var`` partition space fills up, OIM might crash.
