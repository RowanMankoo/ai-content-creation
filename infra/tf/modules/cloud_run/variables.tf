variable "image" {
  description = "The image to use for the instance"
  type        = string
  default     = "debian-cloud/debian-11"
}

variable "service_account_email" {
  description = "The email of the service account to attach to the Cloud Run Job"
  type        = string

}

