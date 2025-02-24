# Define the Cloud Run Job with the service account attached
resource "google_cloud_run_v2_job" "default" {
  name                = "cloudrun-job"
  location            = "us-central1"
  deletion_protection = false

  template {
    template {
      service_account = var.service_account_email

      containers {
        image = var.image
        resources {
          limits = {
            cpu    = "1"
            memory = "4Gi"
          }
        }
      }
    }
  }
}
