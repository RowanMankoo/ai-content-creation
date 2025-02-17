VIDEO_FILE_PATH ?= "/home/rowan/projects/ai-content-creation/mc_parkour.mp4"
AUDIO_FILE_PATH ?= "/home/rowan/projects/ai-content-creation/output.mp3"
SUBTITLE_FILE_PATH ?= "/home/rowan/projects/ai-content-creation/output223.ass"
OUTPUT_FILE_PATH ?= "output_1.mp4"

docker-build:
	docker build -t ai-content-creation/fetch-reddit:latest .

docker-tag:
	docker tag \
	ai-content-creation/fetch-reddit:latest \
	europe-west2-docker.pkg.dev/ai-content-creation-438122/docker-repository/fetch-reddit:latest

docker-run:
	docker run \
	-p 8080:8080 \
	-v /home/rowan/projects/ai-content-creation/service_account.json:/app/key.json \
	-e GOOGLE_APPLICATION_CREDENTIALS="/app/key.json" \
	--env-file .env \
	ai-content-creation/fetch-reddit

docker-push:
	docker push europe-west2-docker.pkg.dev/ai-content-creation-438122/docker-repository/fetch-reddit:latest


ffmpeg-combine:
	ffmpeg \
	-i $(VIDEO_FILE_PATH) \
	-i $(AUDIO_FILE_PATH) \
	-vf subtitles=$(SUBTITLE_FILE_PATH) \
	-map 0:v \
	-map 1:a \
	-shortest \
	-t 20 \
	$(OUTPUT_FILE_PATH)