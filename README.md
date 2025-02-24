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
