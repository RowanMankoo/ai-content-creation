resource "google_cloud_scheduler_job" "trigger_my_job" {
  name        = "trigger-my-job"
  description = "Invoke my-job daily at 5 AM London time"
  schedule    = "0 15 * * *"
  time_zone   = "Europe/London"

  http_target {
    http_method = "POST"
    # point to the jobs.run endpoint for the specific job:
    uri = "https://${module.cloud_run_job__generate_reddit_story_videos.location}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${data.google_project.current.number}/jobs/${module.cloud_run_job__generate_reddit_story_videos.name}:run"

    # supply your override JSON in the body, base64-encoded:
    body = base64encode(jsonencode({
      overrides = {
        containerOverrides = [
          {
            # pass args instead of env
            args = [
              "--input-topic=reddit-stories",
              "--output-bucket=gs://my-output-bucket"
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

  depends_on = [
    google_cloud_run_v2_job.my_job,
    // ensure the Scheduler API is enabled
    google_project_service.cloudscheduler_api
  ]
}