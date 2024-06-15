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
  }

  type = "Opaque"
}
