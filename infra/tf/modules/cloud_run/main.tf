# Define the Cloud Run Job with the service account attached
resource "google_cloud_run_v2_job" "default" {
  name                = "cloudrun-job"
  location            = "us-central1"
  deletion_protection = false

  template {
    template {
      service_account = var.service_account_email
      max_retries     = 1
      timeout         = "3000s"

      containers {
        image = var.image
        resources {
          limits = {
            cpu    = "4"
            memory = "4Gi"
          }
        }
        dynamic "env" {
          for_each = var.env_vars
          content {
            name  = env.value.name
            value = env.value.value
          }
          
        }

        dynamic "env" {
          for_each = var.gcp_secret_manager_env_vars
          content {
            name = env.value.env_name
            value_source {
              secret_key_ref {
                secret  = env.value.secret_name
                version = env.value.version
              }
            }
          }
        }


      }
    }
  }
}
