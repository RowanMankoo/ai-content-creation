

- not saving all artifacts produced by this process as want to save on cloud storage costs
- designed job with requirmtns of being run daily with only a few posts so not very intensive workloads

ffmpeg \
-i {video_file_path} \
-i {audio_file_path} \
-vf subtitles={subtitle_file_path} \
-map 0:v \
-map 1:a \
-shortest \
{output_file_path}

TODO: remove url links all all sorts
TODO: define Post pydantic class and pass it around to diff funcs
TODO: improve error handling
TODO: deal with video being shorter than audio
TODO: add sound
TODO: don't process reddit story if it is longer than threshold, 4096 characters is limit
TODO: allow for differnt videos
TODO: set up videos in bucket and allow access