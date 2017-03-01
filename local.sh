#!/bin/bash

function test() {
cat <<EOF
_________________________________________________________________________________

                                     T E S T
_________________________________________________________________________________
EOF
    IMAGE_NAME=docker_locust
    CONTAINER_NAME=test_docker_locust

    echo "Delete old reports"
    rm -f flake8.log
    rm -f coverage.xml xunit.xml

    echo "Delete docker images"
    docker stop ${CONTAINER_NAME} && docker rm ${CONTAINER_NAME}

    docker build -t ${IMAGE_NAME} .

    echo "Start coding style test (Pep8)"
    docker run --rm ${IMAGE_NAME} /bin/bash -c "flake8 ." > flake8.log

    echo "Start unit test"
    docker run --name ${CONTAINER_NAME} ${IMAGE_NAME} nosetests -v
    docker cp ${CONTAINER_NAME}:/opt/coverage.xml .
    docker cp ${CONTAINER_NAME}:/opt/xunit.xml .
}

function deploy() {
cat <<EOF
_________________________________________________________________________________

                         L O C A L - D E P L O Y M E N T
_________________________________________________________________________________
EOF
    if [ -z "$1" ]; then
        read -p "Target url: " TARGET
    else
        TARGET=$1
    fi

    if [ -z "$2" ]; then
        read -p "Path of load testing script: " FILE
    else
        FILE=$2
    fi

    if [ -z "$3" ]; then
        read -p "Number of slave(s): " SLAVE
    else
        SLAVE=$3
    fi

    if [ -z "$4" ]; then
        read -p "Run type [automatic/manual]: " TYPE
    else
        TYPE=$4
    fi

    if [[ "$TYPE" =~ ^(automatic|Automatic|auto)$ ]]; then
        read -p "Number of users [total users that will be simulated]: " USERS
        read -p "Hatch rate [number of user will be added per second]: " HATCH_RATE
        read -p "Duration [in seconds]: " DURATION
        AUTOMATIC=True
    else
        AUTOMATIC=False
    fi

    echo "-----------------------------------"
    echo "             VARIABLES             "
    echo "-----------------------------------"
    echo "TARGET_URL: $TARGET"
    echo "LOCUST_FILE: $FILE"
    echo "SLAVE NUMBER: $SLAVE"
    echo "RUN_TYPE: $TYPE || automatic=$AUTOMATIC"
    echo "NUMBER OF USERS: $USERS"
    echo "HATCH_RATE: $HATCH_RATE"
    echo "DURATION [in seconds]: $DURATION"
    echo "-----------------------------------"

    echo "Kill old containers if available"
    docker-compose kill

    echo "Remove old containers"
    echo y | docker-compose rm

    echo "Remove old reports"
    rm -rf reports

    echo "Deploy Locust application locally"
    (export TARGET_HOST=$TARGET && export LOCUST_FILE=$FILE && export SLAVE_NUM=$SLAVE && export OAUTH=$OAUTH &&
    export TOKEN_URL=$TOKEN_URL && export OAUTH_SCOPE=$OAUTH_SCOPE && export AUTOMATIC=$AUTOMATIC &&
    export USERS=$USERS && export HATCH_RATE=$HATCH_RATE && export DURATION=$DURATION &&
    docker-compose build && docker-compose up -d)

    echo "Locust application is successfully deployed. you can access http://<your-docker-machine-ip-address>:8089"

    if [[ "$TYPE" =~ ^(automatic|Automatic|auto)$ ]]; then
        sleep 5
        sleep $DURATION
        docker cp docker_locusts_controller:/opt/reports .
    fi
}

$@
