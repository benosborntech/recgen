variable "kubernetes_argocd_namespace" {
  type        = string
  default     = "argocd"
}

variable "kubernetes_app_namespace" {
  type        = string
  default     = "app"
}

variable "digitalocean_token" {
  type = string
}

variable "region" {
  type = string
  default = "syd1"
}