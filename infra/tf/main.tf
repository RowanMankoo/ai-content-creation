resource "google_project_service" "enable_required_apis" {
  for_each = toset([
    "iam.googleapis.com",
    "run.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
    "artifactregistry.googleapis.com",
    "secretmanager.googleapis.com",
  ])
  project = var.project_id
  service = each.value
}

# module "name" {
#   source = "./modules/cloud_run"
#   image = var.image
#   service_account_email = google_service_account.cloud_run_job_service_account.email
  
# }