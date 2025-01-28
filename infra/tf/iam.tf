resource "google_service_account" "cloud_run_invoker_service_account" {
  account_id   = "cloud-run-invoker"
  display_name = "Cloud Run Invoker Service Account"
  depends_on   = [google_project_service.enable_required_apis]
}

resource "google_project_iam_binding" "run_invoker_binding" {
  project = var.project_id
  role    = "roles/run.invoker"

  members = [
    "serviceAccount:${google_service_account.cloud_run_invoker_service_account.email}"
  ]
  depends_on = [google_project_service.enable_required_apis]
}

resource "google_service_account" "gha_service_account" {
  account_id   = "github-actions-sa"
  display_name = "GitHub Actions Service Account"
}

resource "google_project_iam_binding" "gh_service_account_binding" {
  for_each = toset([
    "roles/editor",
    "roles/resourcemanager.projectIamAdmin",
  ])
  project = var.project_id
  role = each.value

  members = [
    "serviceAccount:${google_service_account.gha_service_account.email}"
  ]
  depends_on = [google_project_service.enable_required_apis]
}

resource "google_service_account_key" "gha_service_account_key" {
  service_account_id = google_service_account.gha_service_account.id
  keepers = {
    # Forces recreation if service account changes
    service_account_email = google_service_account.gha_service_account.email
  }
}

resource "google_secret_manager_secret" "gha_service_account_key" {
  secret_id = "gha-service-account-key"
  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "gha_service_account_key_version" {
  secret      = google_secret_manager_secret.gha_service_account_key.id
  secret_data = google_service_account_key.gha_service_account_key.private_key
}
