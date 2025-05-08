resource "google_cloud_scheduler_job" "trigger_generate_reddit_story_videos" {
  name        = var.name
  description = "Trigger Cloud Run Job to generate Reddit story videos"
  schedule    = var.schedule
  time_zone   = "Europe/London"

  http_target {
    http_method = "POST"
    # point to the jobs.run endpoint for the specific job:
    uri = "https://${var.cloud_run_job_location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_number}/jobs/${var.cloud_run_job_name}:run"

    # supply your override JSON in the body, base64-encoded:
    body = base64encode(jsonencode({
      overrides = {
        containerOverrides = [
          {
            args = [
              "--subreddit=${var.subreddit}",
              "--n_posts${var.n_posts}",
              "--n_comments=${var.n_comments}",
              "--time_filter=${var.time_filter}",
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
      service_account_email = var.sa_email
    }
  }

  retry_config {
    retry_count = 1
  }

}
