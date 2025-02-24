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

data "google_secret_manager_secret_version" "gha_service_account_key" {
  secret  = google_secret_manager_secret.gha_service_account_key.id
  version = "latest"
}

resource "github_actions_secret" "gha_service_account" {
  repository      = "ai-content-creation"
  secret_name     = "GCP_SERVICE_ACCOUNT_KEY"
  plaintext_value = data.google_secret_manager_secret_version.gha_service_account_key.secret_data
}

