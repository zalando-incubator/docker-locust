Locust.io Docker Image
======================

[![Build Status](https://travis-ci.org/zalando-incubator/docker-locust.svg?branch=master)](https://travis-ci.org/zalando-incubator/docker-locust)
[![codecov](https://codecov.io/gh/zalando-incubator/docker-locust/branch/master/graph/badge.svg)](https://codecov.io/gh/zalando-incubator/docker-locust)

This docker-locust allows you to run [locust.io] in any CI tools e.g. [Jenkins] and generate HTML report at the end of load test.

Requirement
-----------
1. [docker-compose] version 1.6.0+

Run locust application locally
------------------------------

Run the application with the command:

```bash
local.sh deploy
```

You will be prompted for certain inputs required

```
Target url: https://targeturl.com
Path of load testing script: example/simple.py
Number of slave(s): 5
Run type [automatic/manual]: manual
```

**Or you can simplify it with following command:**

```bash
local.sh deploy https://targeturl.com example/simple.py 5 manual
```

**Note:**
The load test script will be automatically saved in Docker image when the given command above is executed.

Report Generation
-----------------

Simply after load test run, append "/htmlreport" to the URL which will download the report of the recent run. Example:

![][Download report]

Setup in jenkins
----------------

docker-locust can be run automatically by using CI tool like jenkins.

**Sample case:**

- Target url: https://targeturl.com
- Number of slaves: 5
- Number of users [total users that will be simulated]: 100
- Hatch rate [number of user will be added per second]: 5
- Duration [in seconds]: 20

**Steps:**

1. Put following command in "Execute shell" field:

	```bash
	(echo 100 && echo 5 && echo 30) | bash local.sh deploy https://targeturl.com example/simple.py 5 automatic
	```

2. Install [html-publisher-plugin] in jenkins to display load test result. Example configuration in jenkins job:

 ![][HTML-Publisher configuration]

Unit tests
----------

Run the unit tests with this command:

```bash
local.sh test
```

Troubleshooting
---------------

All output from containers can be see by running:

```bash
docker-compose logs -f
```

[locust.io]: <http://locust.io>
[Jenkins]: <https://jenkins.io>
[docker-compose]: <https://docs.docker.com/compose/install/>
[html-publisher-plugin]: <https://wiki.jenkins-ci.org/display/JENKINS/HTML+Publisher+Plugin>
[Download report]: <images/download_report.png> "Download report"
[HTML-Publisher configuration]: <images/usage_html_publisher.png> "Example configuration of HTML Publisher in jenkins job"
