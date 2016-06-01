FROM registry.opensource.zalan.do/stups/ubuntu:15.10-16

EXPOSE 8089
EXPOSE 5557

RUN apt-get update && apt-get install -y python-dev python-zmq python-pip && \
    pip install --upgrade pip locustio requests setuptools boto3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

COPY launch-locust.py /

CMD /launch-locust.py

