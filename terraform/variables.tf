# Misc
variable "digitalocean_token" {
  type = string
}

variable "region" {
  type = string
  default = "syd1"
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