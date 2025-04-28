resource "google_project_iam_binding" "run_job_binding" {
  for_each = toset([
    "roles/storage.objectAdmin",
    "roles/secretmanager.secretAccessor",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
  ])
  project = var.project_id
  role    = each.value

  members = [
    "serviceAccount:${google_service_account.cicd_sa.email}"
  ]
  depends_on = [google_project_service.enable_required_apis]
}
