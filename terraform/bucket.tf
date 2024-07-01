resource "digitalocean_spaces_bucket" "model_bucket" {
  name   = var.bucket_name
  region = var.region
}
