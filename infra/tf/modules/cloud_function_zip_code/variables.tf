variable "name" {
  description = "Base name for the function (used to name the ZIP in GCS)."
  type        = string
}

variable "source_dir" {
  description = "Directory containing your Cloud Function source code."
  type        = string
}

variable "bucket" {
  description = "GCS bucket to upload the ZIP to."
  type        = string
}

variable "object_prefix" {
  description = "Prefix for the object name in GCS."
  type        = string
}
