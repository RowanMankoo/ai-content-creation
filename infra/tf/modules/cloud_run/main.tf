# Define the Cloud Run Job with the service account attached
resource "google_cloud_run_v2_job" "default" {
  name                = "cloudrun-job"
  location            = "us-central1"
  deletion_protection = false

  template {
    template {
      service_account = var.service_account_email
      max_retries     = 3
      timeout         = "600s"

      containers {
        image = var.image
        resources {
          limits = {
            cpu    = "1"
            memory = "4Gi"
          }
        }
        env {
          name = "OPENAI_API_KEY"
          value_source {
            secret_key_ref {
              secret  = "openai-api-key"
              version = "latest"
            }
          }
        }

      }
    }
  }
}
