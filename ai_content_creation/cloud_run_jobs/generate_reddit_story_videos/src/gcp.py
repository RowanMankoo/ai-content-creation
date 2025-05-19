import logging
from datetime import datetime
import os

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

    def upload_text_as_file(self, text: str, destination_blob_name: str):
        """
        Upload a plain text string as a .txt file to a GCP bucket.

        Args:
            text (str): The text content to upload.
            destination_blob_name (str): The destination path in the GCP bucket.
        """
        bucket = self.storage_client.bucket(self.bucket_name)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_string(text, content_type="text/plain")
        logger.info(f"Text uploaded to {destination_blob_name} in bucket {self.bucket_name}.")

    def upload_processsed_video(
        self,
        local_processed_video_path: str,
        video_number: int,
        video_description: str,
        video_tags: list[str],
    ):
        today = datetime.now().strftime("%Y_%m_%d")
        timestamp = datetime.now().strftime("%H%M%S")
        video_subfolder = f"output_{str(video_number)}_{timestamp}"

        video_destination_blob_name = str(
            Path(self.gcp_bucket_video_destination_blob_prefix)
            / Path(f"{today}")
            / Path(video_subfolder)
            / Path("video.mp4")
        )

        video_description = video_description.strip() + ' ' + ", ".join('#'+tag for tag in video_tags)
        video_description_blob_name = str(
            Path(self.gcp_bucket_video_destination_blob_prefix)
            / Path(f"{today}")
            / Path(video_subfolder)
            / Path("video_description.txt")
        )

        # Get the execution ID from the environment variable to use as a form of trace id if we need to debug
        execution_id = os.getenv("CLOUD_RUN_EXECUTION", 'Not set')
        
        self.upload_file(local_processed_video_path, video_destination_blob_name)
        self.upload_text_as_file(
            text=video_description, destination_blob_name=video_description_blob_name
        )
        self.upload_text_as_file(
            text=execution_id, destination_blob_name=f"execution_id.txt"
        )
