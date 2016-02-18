======================
Locust.io Docker Image
======================


``LOCUST_FILE``
    Filename of Locust test. The filename can reference a file on a S3 bucket, example: ``s3://my-bucket/my-folder/locustfile.py``.
``LOCUST_TARGET_HOST``
    Host to load test, example: ``http://example.org``
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
