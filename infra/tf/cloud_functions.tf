
module "zip__upload_to_tiktok" {
  source        = "./modules/cloud_function_zip_code"
  name          = "upload_to_tiktok"
  source_dir    = "${path.root}/../ai_content_creation/cloud_functions/get_tiktok_oauth_token"
  bucket        = google_storage_bucket.storage-bucket.name
  object_prefix = "terraform/cloud_function_zip_code/"
}


resource "google_cloudfunctions2_function" "get_tiktok_oauth_token" {
  name        = "get_tiktok_oauth_token"
  location    = "europe-west2"
  description = "Function to handle TikTok OAuth token retrieval"

  build_config {
    runtime     = "python39"
    entry_point = "fetch_access_token"
    source {
      storage_source {
        bucket = google_storage_bucket.storage-bucket.name
        object = module.zip__upload_to_tiktok.object_name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    available_memory      = "256M"
    timeout_seconds       = 60
    service_account_email = google_service_account.cicd_sa.email

    secret_environment_variables {
      key        = "TIKTOK_CLIENT_ID"
      project_id = var.project_id
      secret     = "tiktok-client-id"
      version    = "latest"
    }

    secret_environment_variables {
      key        = "TIKTOK_CLIENT_SECRET"
      project_id = var.project_id
      secret     = "tiktok-client-secret"
      version    = "latest"
    }

  }
}
