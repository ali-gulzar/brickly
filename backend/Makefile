.PHONY: i-requirements
i-requirements:
	pip install -r requirements.txt

.PHONY: env-variables-export
env-variables-export:
	. env-variables.sh

.PHONY: run-api-locally
run-api-locally: env-variables-export
	OFFLINE=true sls offline --reloadHandler
