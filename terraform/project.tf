resource "digitalocean_project" "project" {
  name      = var.digitalocean_project
  resources = [digitalocean_kubernetes_cluster.cluster.urn]
}
