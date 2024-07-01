resource "digitalocean_project" "project" {
  name      = var.digitalocean_project
  resources = [digitalocean_kubernetes_cluster.cluster.urn, digitalocean_loadbalancer.ingress_load_balancer.urn, digitalocean_spaces_bucket.model_bucket.urn]
}
