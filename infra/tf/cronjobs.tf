module "scheduler_job__generate_reddit_story_videos__AMITheAsshole" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__AMITheAsshole"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 16 * * *"
  subreddit   = "AmITheAsshole"
  time_filter = "day"
}

module "scheduler_job__generate_reddit_story_videos__AITAH" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__AITAH"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 16 * * *"
  subreddit   = "AITAH"
  time_filter = "day"
}

module "scheduler_job__generate_reddit_story_videos__confession" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__confession"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 16 * * *"
  subreddit   = "confession"
  time_filter = "day"
}