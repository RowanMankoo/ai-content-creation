
docker-build:
	docker build -t ai-content-creation/fetch-reddit:latest .

docker-tag:
	docker tag \
	ai-content-creation/fetch-reddit:latest \
	europe-west2-docker.pkg.dev/ai-content-creation-438122/docker-repository/fetch-reddit:latest

docker-run:
	docker run -p 8080:8080 --env-file .env ai-content-creation/fetch-reddit

docker-push:
	docker push europe-west2-docker.pkg.dev/ai-content-creation-438122/docker-repository/fetch-reddit:latest