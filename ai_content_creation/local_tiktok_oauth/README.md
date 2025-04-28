
# TikTok OAuth Integration

This is a Flask app to initialize the OAuth workflow locally for TikTok.

## Steps:
- Create a Sandbox App in TikTok's developer portal.
- The sandbox app allows up to 10 test users. Since we only need one account for posting, we set up a single test user.
- Spin up the Flask app locally and complete the OAuth process with the test user.
- After authentication, you will receive an access token and a refresh token.
   - The access token expires every 24 hours.
   - The refresh token expires after 365 days.
- The refresh token is the important credential we want to keep.
- Run the `python update_bq_db.py --refresh_token '<refresh_token>' --refresh_expires_in '<refresh_expires_in>'` script to store it in BigQuery.
- To get a access_token we trigger our get_tiktok_oauth_token cloud function
   - This queries the BQ DB for the refresh token and hits the oauth endpoint again using this refresh token to get another access token

## Why this setup?
This approach avoids the need to build and maintain a fully-fledged app running 24/7, and skips TikTok’s full app approval process whilst only needing to be ran locally once a year.
