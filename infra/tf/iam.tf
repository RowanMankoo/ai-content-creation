resource "google_project_iam_binding" "run_invoker_binding" {
  project = var.project_id
  role    = "roles/run.invoker"

  members = [
    "serviceAccount:${google_service_account.cloud_run_invoker_service_account.email}"
  ]
  depends_on = [google_project_service.enable_required_apis]
}

resource "google_project_iam_binding" "gh_service_account_binding" {
  for_each = toset([
    "roles/editor",
    "roles/resourcemanager.projectIamAdmin",
    "roles/secretmanager.secretAccessor",
  ])
  project = var.project_id
  role    = each.value

  members = [
    "serviceAccount:${google_service_account.gha_service_account.email}"
  ]
  depends_on = [google_project_service.enable_required_apis]
}

resource "google_project_iam_binding" "run_job_binding" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"

  members = [
    "serviceAccount:${google_service_account.cloud_run_job_service_account.email}"
  ]
  depends_on = [google_project_service.enable_required_apis]
}