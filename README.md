Docker-Locust
=============

[![Build Status](https://travis-ci.org/zalando-incubator/docker-locust.svg?branch=master)](https://travis-ci.org/zalando-incubator/docker-locust)
[![codecov](https://codecov.io/gh/zalando-incubator/docker-locust/branch/master/graph/badge.svg)](https://codecov.io/gh/zalando-incubator/docker-locust)

This docker-locust allows you to run [locust.io] in any CI tools e.g. [Jenkins] and generate HTML report at the end of load test. It is also possible to be deployed in Amazon Web Services to create bigger load.

Requirements
------------
1. [docker engine] version 1.9.1+
2. [docker-compose] version 1.6.0+

Getting Started
---------------

Run the application with the command:

```bash
curl -sSL https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/local.sh | bash -s deploy
```

You will be prompted for certain inputs required

```
Target url: https://targeturl.com
Path of load testing script: simple.py
Number of slave(s): 4
Run type [automatic/manual]: manual
```

**Or you can simplify it with following command:**

```bash
curl -sSL https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/local.sh | bash -s deploy https://targeturl.com simple.py 4 manual
```

Report Generation
-----------------

Please add following lines to your load test script, like [this example].

```
from locust.web import app
from src import report
app.add_url_rule('/htmlreport', 'htmlreport', report.download_report)
```

Simply after load test run, append "/htmlreport" to the URL which will download the report of the recent run. Example:

![][Download report]

Setup in jenkins
----------------

docker-locust can be run automatically by using CI tool like jenkins.

**Sample case:**

- Number of users [total users that will be simulated]: 100
- Hatch rate [number of user will be added per second]: 5
- Duration [in seconds]: 30
- Target url: https://targeturl.com
- Load test script: simple.py
- Number of slaves: 4

**Steps:**

1. Put following command in "Execute shell" field:

	```bash
	(echo 100 && echo 5 && echo 30) | bash local.sh deploy https://targeturl.com simple.py 4 automatic
	```

2. Install [html-publisher-plugin] in jenkins to display load test result. Example configuration in jenkins job:

 ![][HTML-Publisher configuration]

Troubleshooting
---------------

All output from containers can be see by running:

```bash
docker-compose logs -f
```

About the project versioning
----------------------------
A version number is combination between the locust version being supported and patch level, e.g. when a release is 0.7.3-p0, it support locust 0.7.3.

Contributions
-------------
Any feedback or contributions are welcome! Please check our [guidelines].

Unit tests
----------

Run the unit tests with this command:

```bash
local.sh test
```

License
-------
See [License]

Security
--------
See [Security]

[locust.io]: <http://locust.io>
[Jenkins]: <https://jenkins.io>
[docker engine]: <https://docs.docker.com/engine/installation/>
[docker-compose]: <https://docs.docker.com/compose/install/>
[html-publisher-plugin]: <https://wiki.jenkins-ci.org/display/JENKINS/HTML+Publisher+Plugin>
[this example]: <https://github.com/zalando-incubator/docker-locust/blob/master/example/simple.py#L4-L9>
[Download report]: <images/download_report.png> "Download report"
[HTML-Publisher configuration]: <images/usage_html_publisher.png> "Example configuration of HTML Publisher in jenkins job"
[guidelines]: <CONTRIBUTING.md>
[maintainers]: <MAINTAINERS>
[License]: <LICENSE>
[Security]: <SECURITY.md>
