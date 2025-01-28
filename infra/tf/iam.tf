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


