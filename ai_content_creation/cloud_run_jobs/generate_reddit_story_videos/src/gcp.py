import logging
from datetime import datetime

from google.cloud import storage
from pathlib import Path

logger = logging.getLogger(__name__)


class GCPBucketHandler:
    def __init__(self, bucket_name: str, gcp_bucket_video_destination_blob_prefix: str):
        """Initialize the GCP bucket handler."""
        self.bucket_name = bucket_name
        self.storage_client = storage.Client()

        self.gcp_bucket_video_destination_blob_prefix = (
            gcp_bucket_video_destination_blob_prefix
        )

    def download_file(self, source_blob_name: str, destination_file: str) -> Path:
        """
        Download a file from a GCP bucket.

        Args:
            source_blob_name (str): The path of the file in the GCP bucket.
            destination_folder (str): The local folder to save the file.

        Returns:
            Path: The local file path where the file was downloaded.
        """
        logger.info(
            f"Downloading {source_blob_name} from bucket {self.bucket_name} to {destination_file}"
        )

        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(str(destination_file))

        logger.info(f"Downloaded {source_blob_name} to {destination_file}")
        return destination_file

    def upload_file(self, source_file: str, destination_blob_name: str):
        """
        Upload a file to a GCP bucket.

        Args:
            source_file (str): The local file path to upload.
            destination_blob_name (str): The destination path in the GCP bucket.
        """
        source_file_path = Path(source_file)
        if not source_file_path.exists():
            raise FileNotFoundError(f"Source file {source_file} not found.")

        logger.info(
            f"Uploading {source_file} to {destination_blob_name} in bucket {self.bucket_name}"
        )

        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_filename(str(source_file_path))

        logger.info(f"File {source_file} uploaded to {destination_blob_name}.")

    def upload_processsed_video(
        self, local_processed_video_path: str, video_number: int
    ):
        today = datetime.now().strftime("%Y_%m_%d")
        timestamp = datetime.now().strftime("%H%M%S")

        destination_blob_name = str(
            Path(self.gcp_bucket_video_destination_blob_prefix)
            / Path(f"{today}/output_{str(video_number)}_{timestamp}.mp4")
        )
        self.upload_file(local_processed_video_path, destination_blob_name)
