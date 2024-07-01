resource "kubernetes_namespace" "app" {
  metadata {
    name = "app"
  }
}

resource "kubernetes_secret" "secrets" {
  metadata {
    name      = "secrets"
    namespace = kubernetes_namespace.app.metadata[0].name
  }

  data = {
    "openai_key" : var.openai_key
    "spaces_access_key" : var.spaces_access_key
    "spaces_secret_key" : var.spaces_secret_key
    "spaces_endpoint" : var.spaces_endpoint
    "spaces_region" : var.region
  }

  type = "Opaque"
}
