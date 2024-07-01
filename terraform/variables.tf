# Misc
variable "digitalocean_token" {
  type      = string
  sensitive = true
}

variable "digitalocean_user" {
  type = string
}

variable "openai_key" {
  type      = string
  sensitive = true
}

variable "digitalocean_project" {
  type    = string
  default = "recgen"
}

variable "region" {
  type    = string
  default = "syd1"
}

variable "spaces_access_key" {
  type      = string
  sensitive = true
}

variable "spaces_secret_key" {
  type      = string
  sensitive = true
}

variable "spaces_endpoint" {
  type    = string
  default = "syd1.digitaloceanspaces.com"
}

# Cluster
variable "cluster_name" {
  type    = string
  default = "cluster"
}

variable "cluster_min_nodes" {
  type    = number
  default = 2
}

variable "cluster_max_nodes" {
  type    = number
  default = 2
}

variable "cluster_node_size" {
  type    = string
  default = "s-1vcpu-2gb"
}

# Container registry
variable "container_registry_name" {
  type    = string
  default = "recgencr"
}

# Bucket
variable "bucket_name" {
  type    = string
  default = "recgenmodelbucket1412"
}
