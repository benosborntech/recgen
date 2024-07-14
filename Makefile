SHELL := /bin/bash

ENV_FILE = .env
TERRAFORM_DIR = terraform

EVENT_TOPIC = event-topic

init:
	cd $(TERRAFORM_DIR) && terraform init

apply:
	source $(ENV_FILE) && cd $(TERRAFORM_DIR) && terraform apply -var="digitalocean_user=$$DIGITALOCEAN_USER" -var="digitalocean_token=$$DIGITALOCEAN_TOKEN" -var="openai_key=$$OPENAI_KEY" -var="spaces_access_key=$$SPACES_ACCESS_KEY" -var="spaces_secret_key=$$SPACES_SECRET_KEY" -var="spaces_endpoint_origin=$$SPACES_ENDPOINT_ORIGIN"

teardown:
	source $(ENV_FILE) && cd $(TERRAFORM_DIR) && terraform destroy -var="digitalocean_user=$$DIGITALOCEAN_USER" -var="digitalocean_token=$$DIGITALOCEAN_TOKEN" -var="openai_key=$$OPENAI_KEY" -var="spaces_access_key=$$SPACES_ACCESS_KEY" -var="spaces_secret_key=$$SPACES_SECRET_KEY" -var="spaces_endpoint_origin=$$SPACES_ENDPOINT_ORIGIN"

echo:
	source $(ENV_FILE) && echo $$SPACES_ACCESS_KEY && echo $$SPACES_SECRET_KEY

forward-argo:
	kubectl port-forward svc/argocd-server -n argocd 8080:443

forward-submitevent:
	kubectl port-forward svc/submitevent -n app 3000:3000

build-submitevent:
	docker build -t submitevent -f src/docker/submitevent.Dockerfile src

kafka-create-topics:
	kubectl exec -it kafka-0 -n app -- kafka-topics --create --topic $(EVENT_TOPIC) --partitions 1 --replication-factor 1 --bootstrap-server kafka:9092

kafka-topics:
	kubectl exec -it kafka-0 -n app -- kafka-topics --describe --bootstrap-server kafka:9092