resource "google_project_iam_binding" "run_job_binding" {
  for_each = toset([
    "roles/storage.objectAdmin",
    "roles/secretmanager.secretAccessor",
  ])
  project = var.project_id
  role    = each.value

  members = [
    "serviceAccount:${google_service_account.cloud_run_job_service_account.email}"
  ]
  depends_on = [google_project_service.enable_required_apis]
}