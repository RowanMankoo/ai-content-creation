output "object_name" {
  description = "The name of the uploaded ZIP in GCS."
  value       = google_storage_bucket_object.zip.name
}

output "object_md5" {
  description = "MD5 hash of the uploaded ZIP (for cache-busting)."
  value       = data.archive_file.zip.output_md5
}
