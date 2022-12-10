#!/bin/bash

function start_api () {
    source env-variables.sh
    OFFLINE=true sls offline --reloadHandler --stage dev
}

function deploy_api () {
    if [[ -z "${ENVIRONMENT}" ]]; then
        echo "ENVIRONMENT variable not set to deploy!"
    else
        sls deploy --stage ${ENVIRONMENT}
    fi
}

