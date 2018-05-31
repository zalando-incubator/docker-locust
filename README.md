Docker-Locust
=============

[![Build Status](https://travis-ci.org/zalando-incubator/docker-locust.svg?branch=master)](https://travis-ci.org/zalando-incubator/docker-locust)
[![codecov](https://codecov.io/gh/zalando-incubator/docker-locust/branch/master/graph/badge.svg)](https://codecov.io/gh/zalando-incubator/docker-locust)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5a235d56b27647f9b73982933c00314a)](https://www.codacy.com/app/butomo1989/docker-locust?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=zalando-incubator/docker-locust&amp;utm_campaign=Badge_Grade)

The purpose of this project is to provide a ready and easy-to-use version of [locust.io] which also contains additional/useful features that are required.

Architecture
------------
Docker-Locust consist of 3 different roles:

- Master: Instance that will run Locust's web interface where you start and stop the load test and see live statistics.
- Slave: Instance that will simulate users and attack the target url based on user parameters.
- Controller: Instance that will be run for automatic mode and will download the HTML report at the end of load test.

This architecture support following type of deployment:

- single container (standalone mode): If user have only one single machine.
- multiple containers (normal mode): If user have more than one machine and want to create bigger load. This type of deployment might be used in docker-swarm or kubernetes case. An example for deployment in different containers can be seen in [docker-compose].

Key advantages
--------------

1. It allows locust to read load test scenario/script from different resources (any HTTP/HTTPS URL, S3 bucket, and local machine).
2. It has the ability to be run in any CI tool e.g. [Jenkins] (It can start/stop load test automatically) and provides an HTML report at the end of a load test.
3. It is also possible to be deployed in AWS to create bigger load.

Requirements
------------
1. [docker engine] version 1.9.1+
2. [docker-compose] version 1.6.0+ (optional)

Getting Started
---------------

### Single machine / Standalone mode
---

docker-locust will be run as **standalone** version by default. Standalone version is for users who has only 1 single machine.

```bash
bash <(curl -s https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/local.sh) deploy
```

You will be prompted for certains inputs required (You can use [our example] in github as load test script).

```
Target url: https://targeturl.com
Where load test script is stored: https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/simple.py
Number of slave(s): 4
Run type [automatic/manual]: manual
```

*All of it can be simplify in one line:*

```bash
bash <(curl -s https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/local.sh) deploy --target=https://targeturl.com --locust-file=https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/simple.py --slaves=4 --mode=manual
```

It is also possible to run with normal docker command:

```bash
docker run -i --rm -v $PWD/reports:/opt/reports -v ~/.aws:/root/.aws -v $PWD/:/opt/script -v $PWD/credentials:/meta/credentials -p 8089:8089 -e ROLE=standalone -e TARGET_HOST=https://targeturl.com -e LOCUST_FILE=https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/simple.py -e SLAVE_MUL=4 -e AUTOMATIC=False registry.opensource.zalan.do/tip/docker-locust
```

### Multiple machines
---

docker-locust can be run in multiple docker-containers. It is useful for users who has more than one machine to create bigger load. In this point we are using docker-compose, but it is also possible to run it in different ways, e.g. Cloudformation in AWS.

Run the application with the command:

```bash
DOCKER_COMPOSE=true bash <(curl -s https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/local.sh) deploy
```

Read multiple files
-------------------
docker-locust has the ability to read multiple files from s3 or any http/https, e.g. [1 file is the load test file / python file](https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/simple_post.py) and [1 other file is json file](https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/payloads.json) where payloads are stored. Sample command:

```bash
bash <(curl -s https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/local.sh) deploy --target=https://targeturl.com --locust-file=https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/simple_post.py,https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/payloads.json --slaves=4 --mode=manual
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
	curl -O https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/local.sh && DOCKER_COMPOSE=true bash local.sh deploy --target=https://targeturl.com --locust-file=https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/simple.py --slaves=4 --mode=automatic --users=100 --hatch-rate=5 --duration=30
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

Capacity of docker-locust in AWS
--------------------------------

All the data based on load testing against simple [hello-world] application with the default max_wait and min_wait values (1000ms).

|No.   |Group Type   |EC2   |vCPU   |RAM (GiB)   |Clock Speed (GHz)   |Enhanced Networking   |Max total RPS that can be created per 1 slave machine (rough number)   |Price per hour (EU - Frankfurt)   |RPS per cent   |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|1|General Purpose|t2.nano|1|0.5|up to 3.3|-|200|$0.0068|294.12|
|2|General Purpose|t2.micro|1|1|up to 3.3|-|500|$0.014|357.14|
|3|General Purpose|t2.small|1|2|up to 3.3|-|500|$0.027|185.19|
|4|General Purpose|t2.medium|2|4|up to 3.3|-|1100|$0.054|203.7|
|5|General Purpose|t2.large|2|8|up to 3.0|-|1100|$0.108|101.85|
|6|General Purpose|t2.xlarge|4|16|up to 3.0|-|2200|$0.216|101.85|
|7|General Purpose|t2.2xlarge|8|32|up to 3.0|-|4700|$0.432|108.8|
|8|General Purpose|m4.large|2|8|2.4|Yes|700|$0.12|58.33|
|9|General Purpose|m4.xlarge|4|16|2.4|Yes|1500|$0.24|62.5|
|10|General Purpose|m4.2xlarge|8|32|2.4|Yes|2500|$0.48|52.08|
|11|General Purpose|m4.4xlarge|16|64|2.4|Yes|6500|$0.96|67.71|
|12|General Purpose|m4.10xlarge|40|160|2.4|Yes|10000|$2.4|41.67|
|13|General Purpose|m4.16xlarge|64|256|2.3|Yes|17000|$3.84|44.27|
|14|General Purpose|m3.medium|1|3.75|2.5|-|250|$0.079|31.65|
|15|General Purpose|m3.large|2|7.5|2.5|-|600|$0.158|37.97|
|16|General Purpose|m3.xlarge|4|15|2.5|-|1300|$0.315|41.27|
|17|General Purpose|m3.2xlarge|8|30|2.5|-|2600|$0.632|41.14|
|18|Compute Optimized|c4.large|2|3.75|2.9|Yes|800|$0.114|70.18|
|19|Compute Optimized|c4.xlarge|4|7.5|2.9|Yes|1600|$0.227|70.48|
|20|Compute Optimized|c4.2xlarge|8|15|2.9|Yes|2500|$0.454|55.07|
|21|Compute Optimized|c4.4xlarge|16|30|2.9|Yes|6500|$0.909|71.51|
|22|Compute Optimized|c4.8xlarge|36|60|2.9|Yes|12500|$1.817|68.79|
|23|Compute Optimized|c3.large|2|3.75|2.8|Yes|650|$0.129|50.39|
|24|Compute Optimized|c3.xlarge|4|7.5|2.8|Yes|1300|$0.258|50.39|
|25|Compute Optimized|c3.2xlarge|8|15|2.8|Yes|2500|$0.516|48.45|
|26|Compute Optimized|c3.4xlarge|16|30|2.8|Yes|5500|$1.032|53.29|
|27|Compute Optimized|c3.8xlarge|32|60|2.8|Yes|9000|$2.064|43.6|

**NOTE:**

1. Please check [AWS-EC2-Type] and [AWS-EC2-pricing] before use data above, because some of them could be changed time to time.
2. Number of total RPS could be different because of n reasons.

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
[docker-compose]: <docker-compose.yaml>
[Jenkins]: <https://jenkins.io>
[docker engine]: <https://docs.docker.com/engine/installation/>
[docker-compose]: <https://docs.docker.com/compose/install/>
[our example]: <https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/simple.py>
[awscli]: <http://docs.aws.amazon.com/cli/latest/userguide/installing.html>
[html-publisher-plugin]: <https://wiki.jenkins-ci.org/display/JENKINS/HTML+Publisher+Plugin>
[this example]: <https://github.com/zalando-incubator/docker-locust/blob/master/example/simple.py#L4-L9>
[Download report]: <images/download_report.png> "Download report"
[HTML-Publisher configuration]: <images/usage_html_publisher.png> "Example configuration of HTML Publisher in jenkins job"
[hello-world]: <https://github.com/zalando-incubator/docker-locust/blob/master/flask-sample/app.py>
[AWS-EC2-Type]: <https://aws.amazon.com/ec2/instance-types/>
[AWS-EC2-pricing]: <https://aws.amazon.com/ec2/pricing/on-demand/?nc1=h_ls>
[guidelines]: <CONTRIBUTING.md>
[maintainers]: <MAINTAINERS>
[License]: <LICENSE.md>
[Security]: <SECURITY.md>

