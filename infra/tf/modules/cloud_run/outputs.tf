output "instance_id" {
  description = "The ID of the Compute Engine instance"
  value       = google_compute_instance.vm_instance.id
}

output "instance_ip" {
  description = "The public IP of the Compute Engine instance"
  value       = google_compute_instance.vm_instance.network_interface[0].access_config[0].nat_ip
}
