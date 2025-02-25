variable "project_id" {
  description = "The project ID"
  type        = string
  default = "ai-content-creation-438122"
}

variable "cloud_run_job_image__generate_reddit_story_videos" {
  description = "The image to use for the Cloud Run job to generate Reddit story videos"
  type        = string
}