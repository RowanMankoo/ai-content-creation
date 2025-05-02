locals {
  cicd_sa        = "serviceAccount:${google_service_account.cicd_sa.email}"
  cloudbuild_sa  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
  cf_build_sa    = "serviceAccount:${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  rowan_user     = "user:rowan.mankoo@gmail.com"

  cicd_roles        = [
    "roles/storage.objectAdmin",
    "roles/secretmanager.secretAccessor",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/run.admin",
    "roles/iam.serviceAccountTokenCreator",
  ]
  cloudbuild_roles  = [
    "roles/storage.admin",
    "roles/secretmanager.secretAccessor",
    "roles/cloudfunctions.developer",
    "roles/iam.serviceAccountUser",
  ]
  cf_build_sa_roles = [
    "roles/cloudbuild.builds.builder",
    "roles/logging.logWriter",
  ]
  rowan_user_roles = [
    "roles/run.invoker"
  ]
}


resource "google_project_iam_member" "cicd" {
  for_each   = toset(local.cicd_roles)
  project    = var.project_id
  role       = each.value
  member     = local.cicd_sa
  depends_on = [google_project_service.enable_required_apis]
}

resource "google_project_iam_member" "cloudbuild" {
  for_each = toset(local.cloudbuild_roles)
  project  = var.project_id
  role     = each.value
  member   = local.cloudbuild_sa
}

resource "google_project_iam_member" "cf_build_sa" {
  for_each = toset(local.cf_build_sa_roles)
  project  = var.project_id
  role     = each.value
  member   = local.cf_build_sa
}

resource "google_project_iam_member" "rowan_user" {
  for_each = toset(local.rowan_user_roles)
  project  = var.project_id
  role     = each.value
  member   = local.rowan_user
}
