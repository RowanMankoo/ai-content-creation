resource "google_project_service" "enable_required_apis" {
  for_each = toset([
    "iam.googleapis.com",
    "run.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
  ])
  project = var.project_id
  service = each.value
}

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

data "google_secret_manager_secret_version" "gha_service_account_key" {
  secret  = google_secret_manager_secret.gha_service_account_key.id
  version = "latest"
}

resource "github_actions_secret" "gha_service_account" {
  repository      = "ai-content-creation"
  secret_name     = "GCP_SERVICE_ACCOUNT_KEY"
  plaintext_value = data.google_secret_manager_secret_version.gha_service_account_key.secret_data
}

