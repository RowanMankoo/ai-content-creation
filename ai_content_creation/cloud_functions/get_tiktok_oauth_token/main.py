# main.py
import os
import json
import requests
from google.cloud import bigquery
from logging import getLogger

logger = getLogger(__name__)

# Environment
CLIENT_KEY = os.environ["TIKTOK_CLIENT_ID"]
CLIENT_SECRET = os.environ["TIKTOK_CLIENT_SECRET"]
TOKEN_URL = os.environ.get(
    "TIKTOK_TOKEN_URL", "https://open.tiktokapis.com/v2/oauth/token/"
)


bq = bigquery.Client()
TABLE_ID = "ai-content-creation-438122.oauth.tiktok"


def fetch_access_token(request):
    """
    HTTP Cloud Function to refresh TikTok OAuth tokens.
    """
    logger.info("Revieced request for new TikTok OAuth access token")
    select_q = f"""
      SELECT refresh_token 
      FROM `{TABLE_ID}`
      LIMIT 1
    """
    rows = bq.query(select_q).result()
    row = next(rows, None)
    if row is None or not row.refresh_token:
        return ("No refresh token found in BQ", 400)

    refresh_token = row.refresh_token
    logger.info(f"Using refresh token: {refresh_token}")

    payload = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cache-Control": "no-cache",
    }
    logger.info(f"Requesting new access token with payload: {payload}")
    resp = requests.post(TOKEN_URL, headers=headers, data=payload, timeout=10)
    if not resp.ok:
        return (resp.text, resp.status_code)
    oauth_resp = resp.json()
    logger.info(f"Oauth response: {oauth_resp}")

    logger.info("Updating BigQuery table with new refresh token")
    update_q = f"""
      UPDATE `{TABLE_ID}`
      SET
        refresh_token = '{oauth_resp["refresh_token"]}',
        refresh_expires_in = {oauth_resp["refresh_expires_in"]},
        scope = '{oauth_resp["scope"]}',
        updated_at = CURRENT_TIMESTAMP()
      WHERE TRUE
    """
    update_job = bq.query(update_q)
    update_job.result()  # Wait for the job to finish
    logger.debug(f"Updated {update_job.num_dml_affected_rows} rows in BigQuery table")

    return (
        json.dumps(
            {
                "access_token": oauth_resp["access_token"],
                "expires_in": oauth_resp["expires_in"],
            }
        ),
        200,
        {"Content-Type": "application/json"},
    )