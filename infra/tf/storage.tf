resource "google_artifact_registry_repository" "docker_repository" {
  location      = "europe-west2"
  repository_id = "docker-repository"
  format        = "DOCKER"

  docker_config {
    immutable_tags = true
  }

  lifecycle {
    prevent_destroy = true
  }

  depends_on = [google_project_service.enable_required_apis]
}

resource "google_storage_bucket" "storage-bucket" {
  name     = "${var.project_id}-storage-bucket"
  location = "europe-west2"

  lifecycle {
    prevent_destroy = true
  }
}