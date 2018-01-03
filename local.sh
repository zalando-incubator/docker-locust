#!/bin/bash

# Based on https://stackoverflow.com/questions/20137838/catch-abort-signal-on-hudson-in-shell-script
getAbort() {
    echo "ABORT SIGNAL detected! Result won't be collected! terminating locust containers..."
    docker-compose kill
    echo y | docker-compose rm
    echo "containers are terminated"
}
trap 'getAbort; exit' SIGINT SIGTERM

function print_help() {
    echo "Usage:
./local.sh deploy|test --target=<target_url> --locust-file=<file[,file2...]> --slaves=<slaves_amount> --mode=<manual|auto> [--users=<simultaneous_users> --hatch-rate=<added_users_per_second> --duration=<seconds>]

E.g.:
./local.sh deploy --target=https://host-to-test.com --locust-file=https://my.storage/file.py,https://my.storage/payload.json --slaves=4 --mode=manual
./local.sh deploy --target=https://host-to-test.com --locust-file=./local_path.py --slaves=4 --mode=auto --users=1000 --hatch-rate=10 --duration=300

Using positional args:
./local.sh deploy https://host-to-test.com ./local_path.py 4 auto 1000 10 300
"
    exit 1
}

function parse_args() {
  CNT=1
  for i in "$@"; do
    case "${i}" in
      --target=*)
      TARGET="${i#*=}"
      ;;
      --locust-file=*)
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
      --hatch-rate=*)
      HATCH_RATE="${i#*=}"
      ;;
      --duration=*)
      DURATION="${i#*=}"
      ;;
      --help)
      print_help
      ;;
      *)
      ARG[${CNT}]="${i}"
      CNT=$((CNT+1))
      ;;
    esac
  done
  [[ "${CMD}" == "" ]]         && [[ "${ARG[1]}" != "" ]] && CMD="${ARG[1]}"
  [[ "${TARGET}" == "" ]]      && [[ "${ARG[2]}" != "" ]] && TARGET="${ARG[2]}"
  [[ "${LOCUST_FILE}" == "" ]] && [[ "${ARG[3]}" != "" ]] && LOCUST_FILE="${ARG[3]}"
  [[ "${SLAVES}" == "" ]]      && [[ "${ARG[4]}" != "" ]] && SLAVES="${ARG[4]}"
  [[ "${MODE}" == "" ]]        && [[ "${ARG[5]}" != "" ]] && MODE="${ARG[5]}"
  [[ "${USERS}" == "" ]]       && [[ "${ARG[6]}" != "" ]] && USERS="${ARG[6]}"
  [[ "${HATCH_RATE}" == "" ]]  && [[ "${ARG[7]}" != "" ]] && HATCH_RATE="${ARG[7]}"
  [[ "${DURATION}" == "" ]]    && [[ "${ARG[8]}" != "" ]] && DURATION="${ARG[8]}"
}

function test() {
cat <<EOF
_________________________________________________________________________________

                                     T E S T
_________________________________________________________________________________
EOF
    IMAGE_NAME=test_image_locust

    echo "Delete old reports"
    rm -f flake8.log
    rm -f coverage.xml xunit.xml

    docker build -t ${IMAGE_NAME} .

    echo "Start coding style test (Pep8)"
    docker run --rm ${IMAGE_NAME} /bin/bash -c "flake8 ." > flake8.log

    echo "Start unit test"
    docker run --rm -v $PWD:/opt/result ${IMAGE_NAME} nosetests -v
}

function deploy() {
cat <<EOF
_________________________________________________________________________________

                         L O C A L - D E P L O Y M E N T
_________________________________________________________________________________
EOF
    if [ -z $IMAGE ]; then
        IMAGE="registry.opensource.zalan.do/tip/docker-locust"
    fi

    [ -z "$TARGET" ] && read -p "Target url: " TARGET
    [ -z "$LOCUST_FILE" ] && read -p "Where load test script is stored (e.g. https://raw.githubusercontent.com/zalando-incubator/docker-locust/master/example/simple.py): " LOCUST_FILE
    [ -z "$SLAVES" ] && read -p "Number of slave(s): " SLAVES
    [ -z "$MODE" ] && read -p "Run type [automatic/manual]: " MODE

    if [[ "$MODE" =~ ^(automatic|Automatic|auto)$ ]]; then
        [ -z "$USERS" ] && read -p "Number of users [total users that will be simulated]: " USERS
        [ -z "$HATCH_RATE" ] && read -p "Hatch rate [number of user will be added per second]: " HATCH_RATE
        [ -z "$DURATION" ] && read -p "Duration [in seconds]: " DURATION
        AUTOMATIC=true
    else
        AUTOMATIC=false
    fi

    COMPOSE=false
    if [[ "$DOCKER_COMPOSE" =~ ^(True|true|T|t|1)$ ]]; then
        COMPOSE=true
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
    echo "COMPOSE: $COMPOSE"
    echo "----------------------------------------------"

    if $COMPOSE; then
        echo "Run with docker-compose"
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

        echo "Kill old containers if available"
        docker-compose kill

        echo "Remove old containers"
        echo y | docker-compose rm

        echo "Remove old reports"
        rm -rf reports

        echo "Deploy Locust application locally"
        (export IMAGE=$IMAGE && export TARGET_HOST=$TARGET && export LOCUST_FILE=$LOCUST_FILE && export SLAVE_NUM=$SLAVES &&
        export AUTOMATIC=$AUTOMATIC && export USERS=$USERS && export HATCH_RATE=$HATCH_RATE &&
        export DURATION=$DURATION && export OAUTH=$OAUTH && URL=$URL && export SCOPES=$SCOPES && docker-compose up -d)

        echo "Locust application is successfully deployed. you can access http://<docker-host-ip-address>:8089"

        if $AUTOMATIC; then
            sleep 8
            sleep $DURATION
            docker cp docker_locusts_controller:/opt/reports .
        fi
    else
        echo "Run in standalone mode"
        docker run -i --rm -v $PWD/reports:/opt/reports -v ~/.aws:/root/.aws -v $PWD/:/opt/script \
        -v $PWD/credentials:/meta/credentials -p 8089:8089 -e ROLE=standalone -e TARGET_HOST=$TARGET \
        -e LOCUST_FILE=$LOCUST_FILE -e SLAVE_MUL=$SLAVES -e AUTOMATIC=$AUTOMATIC -e USERS=$USERS \
        -e HATCH_RATE=$HATCH_RATE -e DURATION=$DURATION -e OAUTH=$OAUTH -e URL=$URL -e SCOPES=$SCOPES $IMAGE
    fi
}

parse_args $@
[[ "${CMD}" != "" ]] && ${CMD} || print_help
