import argparse
from datetime import datetime
from google.cloud import bigquery

def main(refresh_token: str, refresh_expires_in: str):
    """Replace all rows in our BigQuery table with a new row.
    """
    client = bigquery.Client()
    table_id = "ai-content-creation-438122.oauth.tiktok"

    row_to_insert = [{
        "refresh_token": refresh_token,
        "refresh_expires_in": refresh_expires_in,
        "scope": "user.info.basic",
        "updated_at": datetime.now().isoformat(),
    }]

    # Configure a load job that *replaces* the table
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )

    load_job = client.load_table_from_json(
        row_to_insert,
        table_id,
        job_config=job_config
    )
    load_job.result()  # Wait for the job to finish

    print(f"Table `{table_id}` replaced with {len(row_to_insert)} row(s).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Replace all rows in BigQuery table with one new row.")
    parser.add_argument(
        "--refresh_token", required=True, type=str,
        help="The refresh token to insert."
    )
    parser.add_argument(
        "--refresh_expires_in", required=True, type=str,
        help="The refresh token expiration time."
    )
    args = parser.parse_args()
    main(args.refresh_token, args.refresh_expires_in)
