module "name" {
  source                = "./modules/cloud_run"
  image                 = var.cloud_run_job_image__generate_reddit_story_videos
  service_account_email = google_service_account.cloud_run_job_service_account.email
  env_vars = [ 
    {
      name  = "REDDIT_USER_AGENT"
      value = "MyRedditApp/1.0 by RatedR4Rowan"
    }
  ]


  gcp_secret_manager_env_vars = [
    {
      env_name    = "OPENAI_API_KEY"
      secret_name = "openai-api-key"
      version     = "latest"
    },
    {
      env_name    = "REDDIT_CLIENT_ID"
      secret_name = "reddit-client-id"
      version     = "latest"
    },
    {
      env_name    = "REDDIT_SECRET_KEY"
      secret_name = "reddit-secret-key"
      version     = "latest"
    },
  ]
}
