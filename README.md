# ai-content-creation

1. build docker images
2. push to GCP Registry
3. apply terraform 


apt-get -y install ffmpeg imagemagick


ffmpeg -i mc_parkour.mp4 -i output.mp3 -vf subtitles=subtitles.ass -map 0:v -map 1:a -t 30 -c:v libx264 -c:a aac -strict -2 -shortest output_with_subtitles_and_audio.mp4


steps:
1. get story
2. 



Changes to infra first in their own PR's
- add new tfvar under terraform.tfvars `cloud_run_job_image__<cloud_run_job_name>` put any image path this will update in CICD on PR creation
- add another cloud run job under cloud_run_jobs.tf and use image var


Manual workflow dispatch to check what chnaegs terraform will do

## Local tf setup 

To use terraform commands locally you need to set up GH auth as follows:

1. `unset GITHUB_TOKEN`
2. `gh auth login`


only 15-25 apps are have been audited and clear for use by tiktok of their content posting api

youtube is easier to verify an app