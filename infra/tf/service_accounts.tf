resource "google_service_account" "cloud_run_job_service_account" {
  account_id   = "cloud-run-job-sa"
  display_name = "Cloud Run Job Service Account"
}

resource "google_service_account" "gha_service_account" {
  account_id   = "github-actions-sa"
  display_name = "GitHub Actions Service Account"
}

resource "google_service_account_key" "gha_service_account_key" {
  service_account_id = google_service_account.gha_service_account.id
  keepers = {
    # Forces recreation if service account changes
    service_account_email = google_service_account.gha_service_account.email
  }
}