SHELL := /bin/bash

ENV_FILE = ".env"
TERRAFORM_DIR = "terraform"

init:
	cd $(TERRAFORM_DIR) && terraform init

apply:
	source $(ENV_FILE) && cd $(TERRAFORM_DIR) && terraform apply -var="digitalocean_user=$$DIGITALOCEAN_USER" -var="digitalocean_token=$$DIGITALOCEAN_TOKEN"

forward-argo:
	kubectl port-forward svc/argocd-server -n argocd 8080:443

forward-submitevent:
	kubectl port-forward svc/submitevent -n app 3000:3000

build-submitevent:
	docker build -t submitevent -f src/docker/submitevent.Dockerfile src

kafka-create-topics:
	kubectl exec -it kafka-0 -n app -- kafka-topics --create --topic event-topic --partitions 1 --replication-factor 1 --bootstrap-server kafka:29092

kafka-list-topics:
	kubectl exec -it kafka-0 -n app -- kafka-topics --list --bootstrap-server kafka:29092