# Docker-Locust's Anonymous Aggregate User Behaviour Analytics
Docker-Locust has begun gathering anonymous aggregate user behaviour analytics and reporting these to Google Analytics. You are notified about this when you start Docker-Locust.

## Why?
Docker-Locust is provided free of charge for our internal and external users and we don't have direct communication with its users nor time resources to ask directly for their feedback. As a result, we now use anonymous aggregate user analytics to help us understand how Docker-Locust is being used, the most common used features based on how, where and when people use it. With this information we can prioritize some features over other ones.

## What?
Docker-Locust's analytics record some shared information for every event:

- The Google Analytics version i.e. `1` (https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#v)
- The Google Analytics anonymous IP setting is enabled i.e. `1` (https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#aip)
- The Docker-Locust analytics tracking ID e.g. `UA-110383676-1` (https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#tid)
- The release version of machine, e.g. `Linux_version_4.4.16-boot2docker_(gcc_version_4.9.2_(Debian_4.9.2-10)_)_#1_SMP_Fri_Jul_29_00:13:24_UTC_2016` This does not allow us to track individual users but does enable us to accurately measure user counts vs. event counts (https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#cid)
- Docker-Locust analytics hit type, e.g. `event` (https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#t)
- User type, e.g. `external` (https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#ec)
- Description will contains information about platform and target host. This information will be get only from our internal users or users who load test target host which contains word 'zalan.do' or 'zalando'. (https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#el)
- Docker-Locust application name, e.g. `docker-locust` (https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#an)
- Docker-Locust application version, e.g. `0.8.1-p1` (https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#av)

With the recorded information, it is not possible for us to match any particular real user.

As far as we can tell it would be impossible for Google to match the randomly generated analytics user ID to any other Google Analytics user ID. If Google turned evil the only thing they could do would be to lie about anonymising IP addresses and attempt to match users based on IP addresses.

## When/Where?
Docker-Locust's analytics are sent throughout Docker-Locust's execution to Google Analytics over HTTPS.

## Who?
Docker-Locust's analytics are accessible to Docker-Locust's current maintainers. Contact [@scherniavsky](https://github.com/scherniavsky) if you are a maintainer and need access.

## How?
The code is viewable in [this lines](./src/app.py#L174-L239).

The code is implemented in try except block. If it fails, it will skip it.

## Opting out before starting Docker-Locust
Docker-Locust analytics helps us, maintainers and leaving it on is appreciated. However, if you want to opt out and not send any information, you can do this by using passing the following parameter at start time:

```sh
SEND_ANONYMOUS_USAGE_INFO=false bash <(curl -s https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/local.sh) deploy
```

## Disclaimer
This document and the implementation are based on the great idea implemented by [Homebrew](https://github.com/Homebrew/brew/blob/master/docs/Analytics.md)
