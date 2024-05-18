# Misc
variable "digitalocean_token" {
  type = string
}

variable "region" {
  type = string
  default = "syd1"
}

# Kubernetes
variable "kubernetes_argocd_namespace" {
  type        = string
  default     = "argocd"
}

variable "kubernetes_app_namespace" {
  type        = string
  default     = "app"
}

# Cluster
variable "cluster_name" {
  type        = string
  default = "cluster"
}

variable "cluster_min_nodes" {
  type        = number
  default     = 1
}

variable "cluster_max_nodes" {
  type        = number
  default     = 1
}

variable "cluster_node_size" {
  type        = string
  default     = "s-1vcpu-2gb"
}