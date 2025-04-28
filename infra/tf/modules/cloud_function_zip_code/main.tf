data "archive_file" "zip" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "${path.module}/${var.name}.zip"
}

resource "google_storage_bucket_object" "zip" {
  bucket = var.bucket
  name   = "${var.object_prefix}${var.name}-${data.archive_file.zip.output_md5}.zip"
  source = data.archive_file.zip.output_path
}
