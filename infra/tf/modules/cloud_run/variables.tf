variable "image" {
  description = "The image to use for the instance"
  type        = string
  default     = "debian-cloud/debian-11"
}

variable "service_account_email" {
  description = "The email of the service account to attach to the Cloud Run Job"
  type        = string

}

variable "env_vars" {
  description = "List of environment variables to attach to the Cloud Run job"
  type        = list(object({
    name  = string
    value = string
  }))
  default = []
}

variable "gcp_secret_manager_env_vars" {
  description = "List of secrets to be attached to the Cloud Run job as env vars"
  type = list(object({
    env_name = string   # Environment variable name in the container
    secret_name   = string   # The secret resource name in GCP Secret Manager
    version  = string   # The version of the secret to use (e.g., "latest")
  }))
  default = []
}
