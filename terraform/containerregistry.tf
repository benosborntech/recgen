resource "digitalocean_container_registry" "container_registry" {
  name                   = var.container_registry_name
  subscription_tier_slug = "basic"
}

resource "kubernetes_secret" "docker_registry_secret" {
  metadata {
    name      = "regcred"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "registry.digitalocean.com" = {
          auth = base64encode("${var.digitalocean_user}:${var.digitalocean_token}")
        }
      }
    })
  }

  type = "kubernetes.io/dockerconfigjson"
}
