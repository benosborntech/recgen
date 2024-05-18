resource "digitalocean_kubernetes_cluster" "cluster" {
  name   = var.cluster_name
  region = var.region
  version = "1.29.1-do.0"

  node_pool {
    name       = "${var.cluster_name}-worker-pool"
    size       = var.cluster_node_size
    auto_scale = true
    min_nodes  = var.cluster_min_nodes
    max_nodes  = var.cluster_max_nodes
  }
}