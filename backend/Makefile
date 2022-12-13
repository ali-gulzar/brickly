.PHONY: i-requirements
i-requirements:
	pip install -r requirements.txt

.PHONY: run-api-locally
run-api-locally:
	. scripts.sh; start_api

.PHONY: start-dynamo-db
start-dynamo-db:
	. scripts.sh; start_dynamo_db

.PHONY: deploy
deploy:
	. scripts.sh; deploy_api

.PHONY: format
format:
	black . && isort .
