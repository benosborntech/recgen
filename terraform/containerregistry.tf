resource "digitalocean_container_registry" "container_registry" {
  name                   = var.container_registry_name
  subscription_tier_slug = "basic"
}
