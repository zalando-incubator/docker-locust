FROM registry.opensource.zalan.do/stups/ubuntu:18.04-15

#=======================
# General Configuration
#=======================
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
RUN apt-get update && apt-get install -y jq python3-dev python3-zmq python3-pip && rm -rf /var/lib/apt/lists/*

#==============
# Expose Ports
#==============
EXPOSE 8089
EXPOSE 5557
EXPOSE 5558

#======================
# Install dependencies
#======================
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

#=====================
# Start docker-locust
#=====================
COPY src /opt/src/
COPY setup.cfg /opt/
RUN mkdir /opt/result /opt/reports
RUN ln -s /opt/src/app.py /usr/local/bin/locust-wrapper
WORKDIR /opt
ENV PYTHONPATH /opt
ARG DL_IMAGE_VERSION=latest
ENV DL_IMAGE_VERSION=$DL_IMAGE_VERSION \
    SEND_ANONYMOUS_USAGE_INFO=true

CMD ["locust-wrapper"]