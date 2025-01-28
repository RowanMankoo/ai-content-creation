resource "google_cloud_run_v2_service" "default" {
  name     = "SERVICE"
  location = "REGION"
  client   = "terraform"

  template {
    containers {
      image = "IMAGE"
    }
  }
}