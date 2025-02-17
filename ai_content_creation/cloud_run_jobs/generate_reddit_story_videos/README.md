

- not saving all artifacts produced by this process as want to save on cloud storage costs
- 

ffmpeg \
-i {video_file_path} \
-i {audio_file_path} \
-vf subtitles={subtitle_file_path} \
-map 0:v \
-map 1:a \
-shortest \
{output_file_path}