module "scheduler_job__generate_reddit_story_videos__AMITheAsshole" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__AMITheAsshole"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 6 * * 0"
  subreddit   = "AmITheAsshole"
  time_filter = "week"
  n_posts     = 3
}

module "scheduler_job__generate_reddit_story_videos__AITAH" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__AITAH"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 6 * * 1"
  subreddit   = "AITAH"
  time_filter = "week"
  n_posts     = 3
}

module "scheduler_job__generate_reddit_story_videos__confession" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__confession"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 6 * * 2"
  subreddit   = "confession"
  time_filter = "week"
  n_posts     = 3
}

module "scheduler_job__generate_reddit_story_videos__TrueOffMyChest" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__TrueOffMyChest"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 6 * * 3"
  subreddit   = "TrueOffMyChest"
  time_filter = "week"
  n_posts     = 3
}

module "scheduler_job__generate_reddit_story_videos__PointlessStories" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__PointlessStories"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 6 * * 4"
  subreddit   = "PointlessStories"
  time_filter = "week"
  n_posts     = 3
}


module "scheduler_job__generate_reddit_story_videos__Relationships" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__Relationships"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 6 * * 5"
  subreddit   = "Relationships"
  time_filter = "week"
  n_posts     = 3
}

module "scheduler_job__generate_reddit_story_videos__relationship_advice" {
  source = "./modules/generate_reddit_story_videos_cronjob"

  name        = "scheduler_job__generate_reddit_story_videos__relationship_advice"
  cloud_run_job_name = module.cloud_run_job__generate_reddit_story_videos.name
  cloud_run_job_location = module.cloud_run_job__generate_reddit_story_videos.location
  sa_email = google_service_account.cicd_sa.email
  project_number = data.google_project.project.number
  schedule    = "0 6 * * 6"
  subreddit   = "relationship_advice"
  time_filter = "week"
  n_posts     = 3
}