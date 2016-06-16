======================
Locust.io Docker Image
======================

This Docker image allows you to run the `Locust.io load testing tool`_. It's different from other Locust-related Docker images in that it loads the actual test execution script (locustfile.py) from AWS S3. I.e., you can use the same Docker image for different load-testing scenarios without providing the locustfile.py "locally" on the server (or in the Docker image itself).

Starting a Locust Master
========================

Set the ``LOCUST_MASTER`` environment variable to a non-empty value to start a master:

.. code-block::

    $ docker run -it --net=host -e LOCUST_MASTER=true -e LOCUST_FILE=s3://mybucket/mypath/locustfile.py registry.opensource.zalan.do/stups/locust:0.1


Starting a Locust Slave
=======================

Set the ``LOCUST_MASTER_HOST`` environment variable to the master's address (IP) to
start slave processes:

.. code-block::

    $ docker run -it --net=host -e LOCUST_MASTER_HOST=127.0.0.1 -e LOCUST_FILE=s3://mybucket/mypath/locustfile.py registry.opensource.zalan.do/stups/locust:0.1


Configuration Options
=====================

``LOCUST_FILE``
    Filename of Locust test. The filename can reference a file on a S3 bucket. For example: ``s3://my-bucket/my-folder/locustfile.py``.
``LOCUST_TARGET_HOST``
    Host to load test. Example: ``http://example.org``
``LOCUST_MASTER``
    Run as Locust master
``LOCUST_MASTER_HOST``
    Host of Locust master
``LOCUST_CLIENTS``
    Number of users
``LOCUST_HATCH_RATE``
    Number of new users per second
``LOCUST_SLAVE_COUNT``
    Number of slaves to spawn (defaults to number of CPU cores)


.. _Locust.io load testing tool: http://locust.io

