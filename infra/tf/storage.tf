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

resource "google_bigquery_dataset" "dataset" {
  dataset_id = "oauth"
  location   = "europe-west2"
}

resource "google_bigquery_table" "table" {
  dataset_id  = google_bigquery_dataset.dataset.dataset_id
  table_id    = "tiktok"
  description = "Table for storing TikTok refresh token"

  deletion_protection = false

  schema = jsonencode([
    {
      name = "refresh_token"
      type = "STRING"
    },
    {
      name = "refresh_expires_in"
      type = "STRING"
    },
    {
      name = "scope"
      type = "STRING"
    },
    {
      name = "updated_at"
      type = "TIMESTAMP"
    },
  ])
}
