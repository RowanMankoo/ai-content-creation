resource "google_cloud_scheduler_job" "trigger_generate_reddit_story_videos" {
  name        = "trigger_generate_reddit_story_videos"
  description = "Trigger Cloud Run Job to generate Reddit story videos"
  schedule    = "06 18 * * *"
  time_zone   = "Europe/London"

  http_target {
    http_method = "POST"
    # point to the jobs.run endpoint for the specific job:
    uri = "https://${module.cloud_run_job__generate_reddit_story_videos.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${data.google_project.project.number}/jobs/${module.cloud_run_job__generate_reddit_story_videos.name}:run"

    # supply your override JSON in the body, base64-encoded:
    body = base64encode(jsonencode({
      overrides = {
        containerOverrides = [
          {
            args = [
              "--subreddit=AmITheAsshole",
            ]
          }
        ]
      }
    }))

    headers = {
      "Content-Type" = "application/json"
    }

    oauth_token {
      # service account used by Scheduler to invoke the job
      service_account_email = google_service_account.cicd_sa.email
    }
  }

  # optional: retry on failure up to 3 times
  retry_config {
    retry_count = 3
  }

}