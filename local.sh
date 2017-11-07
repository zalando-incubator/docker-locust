#!/bin/bash

# Based on https://stackoverflow.com/questions/20137838/catch-abort-signal-on-hudson-in-shell-script
getAbort() {
    echo "ABORT SIGNAL detected! Result won't be collected! terminating locust containers..."
    docker-compose kill
    echo y | docker-compose rm
    echo "containers are terminated"
}
trap 'getAbort; exit' SIGINT SIGTERM

function parse_args() {
  CNT=1
  for i in "$@"; do
    case "${i}" in
      --target=*)
      TARGET="${i#*=}"
      ;;
      --locust_file=*)
      LOCUST_FILE="${i#*=}"
      ;;
      --slaves=*)
      SLAVES="${i#*=}"
      ;;
      --mode=*)
      MODE="${i#*=}"
      ;;
      --users=*)
      USERS="${i#*=}"
      ;;
      --hatch_rate=*)
      HATCH_RATE="${i#*=}"
      ;;
      --duration=*)
      DURATION="${i#*=}"
      ;;
      *)
      ARG[${CNT}]="${i}"
      CNT=$((CNT+1))
      ;;
    esac
  done
  [[ "${TARGET}" == "" ]] && [[ "${ARG[1]}" != "" ]] && TARGET="${ARG[1]}"
  [[ "${LOCUST_FILE}" == "" ]] && [[ "${ARG[2]}" != "" ]] && LOCUST_FILE="${ARG[2]}"
  [[ "${SLAVES}" == "" ]] && [[ "${ARG[3]}" != "" ]] && SLAVES="${ARG[3]}"
  [[ "${MODE}" == "" ]] && [[ "${ARG[4]}" != "" ]] && MODE="${ARG[4]}"
  [[ "${USERS}" == "" ]] && [[ "${ARG[5]}" != "" ]] && USERS="${ARG[5]}"
  [[ "${HATCH_RATE}" == "" ]] && [[ "${ARG[6]}" != "" ]] && HATCH_RATE="${ARG[6]}"
  [[ "${DURATION}" == "" ]] && [[ "${ARG[7]}" != "" ]] && DURATION="${ARG[7]}"
}

function test() {
cat <<EOF
_________________________________________________________________________________

                                     T E S T
_________________________________________________________________________________
EOF
    IMAGE_NAME=test_image_locust
    CONTAINER_NAME=test_container_locust

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
    parse_args $@

    IMAGE="registry.opensource.zalan.do/tip/docker-locust"
    echo "----------------------------------------------"       
    echo "             Download compose file            "     
    echo "----------------------------------------------"     
    COMPOSE_FILE=docker-compose.yaml      
    if [ ! -f $COMPOSE_FILE ]; then       
        curl -o $COMPOSE_FILE https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/docker-compose.yaml        
        echo -e "Download completed! \xE2\x9C\x94"        
    else      
        echo -e 'File is found, download is not needed! \xE2\x9C\x94'     
    fi

    [ -z "$TARGET" ] && read -p "Target url: " TARGET
    [ -z "$LOCUST_FILE" ] && read -p "Where load test script is stored (e.g. https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/simple.py): " LOCUST_FILE
    [ -z "$SLAVES" ] && read -p "Number of slave(s): " SLAVES
    [ -z "$MODE" ] && read -p "Run type [automatic/manual]: " MODE

    if [[ "$MODE" =~ ^(automatic|Automatic|auto)$ ]]; then
        [ -z "$USERS" ] && read -p "Number of users [total users that will be simulated]: " USERS
        [ -z "$HATCH_RATE" ] && read -p "Hatch rate [number of user will be added per second]: " HATCH_RATE
        [ -z "$DURATION" ] && read -p "Duration [in seconds]: " DURATION
        AUTOMATIC=True
    else
        AUTOMATIC=False
    fi

    echo "----------------------------------------------"
    echo "                   VARIABLES                  "
    echo "----------------------------------------------"
    echo "TARGET_URL: $TARGET"
    echo "LOCUST_FILE: $LOCUST_FILE"
    echo "SLAVES NUMBER: $SLAVES"
    echo "RUN_TYPE: $MODE || automatic=$AUTOMATIC"
    echo "NUMBER OF USERS: $USERS"
    echo "HATCH_RATE: $HATCH_RATE"
    echo "DURATION [in seconds]: $DURATION"
    echo "----------------------------------------------"

    echo "Kill old containers if available"
    docker-compose kill

    echo "Remove old containers"
    echo y | docker-compose rm

    echo "Remove old reports"
    rm -rf reports

    echo "Deploy Locust application locally"
    (export TARGET_HOST=$TARGET && export LOCUST_FILE=$LOCUST_FILE && export SLAVE_NUM=$SLAVES &&
    export AUTOMATIC=$AUTOMATIC && export USERS=$USERS && export HATCH_RATE=$HATCH_RATE &&
    export DURATION=$DURATION && docker-compose up -d)

    echo "Locust application is successfully deployed. you can access http://<docker-host-ip-address>:8089"

    if [[ "$MODE" =~ ^(automatic|Automatic|auto)$ ]]; then
        sleep 5
        sleep $DURATION
        docker cp docker_locusts_controller:/opt/reports .
    fi
}

$@
