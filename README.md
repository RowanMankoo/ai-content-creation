# ai-content-creation

This repository automates the creation of AI-generated videos for platforms like TikTok and YouTube Shorts, in the hope to gain profit off of the monisation of the videos. 

[Here](https://www.tiktok.com/@xcite9) is the TikTok account where these videos are getting posted to.

## Overview

A scheduled Cloud Run job scrapes posts from a "storytime" subreddit each day. For each post:

1. The text is converted to audio using a TTS model.
2. The audio is transcribed using OpenAI's Whisper model for accurate subtitles.
3. The audio, subtitles, and a background video are combined into a final video.
4. The resulting video is saved to a GCS bucket and manually uploaded to TikTok.

The job runs daily via a scheduled Cloud Scheduler trigger (cron job).

---

## CI/CD

- On push to `main`, all Terraform changes are automatically applied.
- On pull request creation, if changes are detected in the `cloud_run_jobs` folder:
  - A new Docker image is built with the changes.
  - The image is pushed to Artifact Registry.
  - CI/CD updates `terraform.tfvars` with the new image reference.
- A manual workflow dispatch is available to run `terraform plan` if needed.

---

## Adding a New Cloud Run Job

1. Create a new folder under `ai_content_creation/cloud_run_jobs/<job_name>`.
2. Add a new image variable in `terraform.tfvars`:  
   `cloud_run_job_image__<job_name> = "<image_path>"`  
   (This will be auto-updated in CI/CD on PR creation.)
3. Define the Cloud Run job in `cloud_run_jobs.tf` and reference the image variable.

---

## Local Terraform Setup

To run Terraform locally:

```bash
unset GITHUB_TOKEN
gh auth login
```

---

## TikTok API Limitations

Using the TikTok content posting API requires:

- A registered website
- An audit process with TikTok

As of now, only 15–25 apps have been approved. A local sandbox test allowed linking one account, but only private videos could be posted—not public.

See more details in `ai_content_creation/local_tiktok_oauth/README.md`.

---

## YouTube API

YouTube’s video posting API also requires approval, but access is generally easier to obtain compared to TikTok.
