#!/bin/sh
source env-variables.sh && \
    OFFLINE=true sls offline --reloadHandler --stage dev