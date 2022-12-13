#!/bin/bash

function start_api () {
    . ./env-variables.sh
    OFFLINE=true sls offline --reloadHandler --stage dev
}

function deploy_api () {
    if [[ -z "${ENVIRONMENT}" ]]; then
        echo "ENVIRONMENT variable not set to deploy!"
    else
        sls deploy --stage ${ENVIRONMENT}
    fi
}

function start_dynamo_db () {
    . ./env-variables.sh
    OFFLINE=true sls dynamodb start --stage dev
}