resource "google_service_account" "cicd_sa" {
  account_id   = "cloud-run-job-sa"
  display_name = "Cloud Run Job Service Account"
}

# Manually defined via GCP Console
data "google_service_account" "gha_service_account" {
  account_id = "github-actions-sa"
  project    = var.project_id
}

resource "google_service_account_key" "gha_service_account_key" {
  service_account_id = data.google_service_account.gha_service_account.id
  keepers = {
    # Forces recreation if service account changes
    service_account_email = data.google_service_account.gha_service_account.email
  }
}
