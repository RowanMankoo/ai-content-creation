variable "name" {
  description = "Name of the Cloud Scheduler job."
  type        = string
}

variable "cloud_run_job_name" {
  description = "Name of the Cloud Run job to trigger."
  type        = string
}

variable "cloud_run_job_location" {
  description = "Location of the Cloud Run job to trigger."
  type        = string
}

variable "sa_email" {
  description = "Name of the service account to use for the Cloud Scheduler job."
  type        = string
  default     = "cicd-sa"
}

variable "project_number" {
  description = "Project number of the GCP project."
  type        = string
}

variable "schedule" {
  description = "cron schedule for the job of the form \"* * * * *\" (e.g. \"0 12 * * *\" for every day at noon)."
  type        = string
}

variable "subreddit" {
  description = "Subreddit to scrape."
  type        = string
}


variable "time_filter" {
  description = "Time filter for the top posts to scrape."
  type        = string
}

variable "n_posts" {
  description = "Number of posts to scrape."
  type        = number
  default     = 1

}

variable "n_comments" {
  description = "Number of posts to scrape."
  type        = number
  default     = 1

}
