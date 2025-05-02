provider "google" {
  project = var.project_id
  region  = "europe-west2-a"

}

provider "github" {
  owner = "RowanMankoo"
}

terraform {
  backend "gcs" {
    bucket = "ai-content-creation-438122-storage-bucket"
    prefix = "terraform/state/terraform.tfstate"

  }
}

data "google_project" "project" {
  project_id = var.project_id
}
