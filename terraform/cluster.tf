resource "digitalocean_kubernetes_cluster" "cluster" {
  name   = var.cluster_name
  region = var.region
  version = "1.22.8-do.1"

  node_pool {
    name       = "${var.cluster_name}-default-pool"
    size       = var.cluster_min_nodes
    auto_scale = true
    min_nodes  = var.cluster_min_nodes
    max_nodes  = var.cluster_max_nodes
  }
}