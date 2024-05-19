resource "digitalocean_container_registry" "submitevent_container_registry" {
  name                   = var.submitevent_container_registry_name
  subscription_tier_slug = "starter"
}
