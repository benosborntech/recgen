SHELL := /bin/bash

ENV_FILE = ".env"
TERRAFORM_DIR = "terraform"

init:
	cd $(TERRAFORM_DIR) && terraform init

apply:
	source $(ENV_FILE) && cd $(TERRAFORM_DIR) && terraform apply -var="digitalocean_token=$$DIGITALOCEAN_TOKEN"

argo:
	kubectl port-forward svc/argocd-server -n argocd 8080:443