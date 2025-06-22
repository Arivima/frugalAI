.PHONY: streamlit api up
PATH_SERVICE_ACCOUNT_KEY=frugalai-2025-080c1bf50146.json

GCP_PROJECT_ID=frugalai-2025

TAG=latest
ARTIFACT_REPOSITORY=frugalai-repo
ARTIFACT_REGION=europe-west9
# ARTIFACT_URI=europe-west9-docker.pkg.dev/frugalai-2025/frugalai-repo
# ARTIFACT_IMAGE=europe-west9-docker.pkg.dev/frugalai-2025/frugalai-repo/front:latest
ARTIFACT_URI = $(ARTIFACT_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(ARTIFACT_REPOSITORY)

# stop all containers
docker_stop:
	@echo Stopping all running containers
	docker ps -q | xargs -r docker stop

# clean all dangling ressources
docker_cleanup:
	@echo Cleaning all unused ressources
	docker system prune -f

# clean all ressources
docker_force_cleanup: docker_stop docker_cleanup
	@echo Stopping all running containers and cleaning all ressources

# launches the app
docker_up: docker_force_cleanup api_docker_run front_docker_run
	@echo api available at http://localhost:8080/
	@echo front available at http://localhost:8502/


################################# API #################################

API_DOCKER_IMAGE_NAME=api
API_DOCKER_CONTAINER_NAME='container-api'

# test in local
api_local:
	UV_ENV_FILE=".env" uv run uvicorn api.app.main:app --host 0.0.0.0 --port 8080 --reload

# stop the container and remove the image
api_docker_down:
	-docker rm -f $(API_DOCKER_CONTAINER_NAME) 2>/dev/null
	-docker rmi $(API_DOCKER_IMAGE_NAME) 2>/dev/null

# build docker image
api_docker_build: api_docker_down
	@echo Building image "$(API_DOCKER_IMAGE_NAME)"
	docker build --no-cache -f api/Dockerfile -t $(API_DOCKER_IMAGE_NAME) . 

# testing inside the container
api_docker_run_detached: api_docker_down api_docker_build
	-docker rm -f $(API_DOCKER_CONTAINER_NAME) 2>/dev/null
	@echo Running container "$(API_DOCKER_CONTAINER_NAME)"
	docker run -d \
		--name $(API_DOCKER_CONTAINER_NAME) \
		--env-file .env \
		-e GOOGLE_APPLICATION_CREDENTIALS='/app/service-account.json' \
		-v $(shell pwd)/$(PATH_SERVICE_ACCOUNT_KEY):/app/service-account.json \
		--entrypoint=sh \
		-p 8080:8080 \
		$(API_DOCKER_IMAGE_NAME) \
		-c "tail -f /dev/null"
	@echo Entering container "$(API_DOCKER_CONTAINER_NAME)"
	docker exec -it $(API_DOCKER_CONTAINER_NAME) sh

# WHEN INSIDE THE CONTAINER, TEST
# tree
# printenv | grep GCP
# ls -l /app/service-account.json
# uvicorn api.app.main:app --host 0.0.0.0 --port 8080


# run docker container
api_docker_run: api_docker_build
	-docker rm -f $(API_DOCKER_CONTAINER_NAME) 2>/dev/null
	@echo Running container "$(API_DOCKER_CONTAINER_NAME)"
	docker run -d \
		--name $(API_DOCKER_CONTAINER_NAME) \
		--env-file .env \
		-e GOOGLE_APPLICATION_CREDENTIALS='/app/service-account.json' \
		-v $(shell pwd)/$(PATH_SERVICE_ACCOUNT_KEY):/app/service-account.json \
		-p 8080:8080 \
		$(API_DOCKER_IMAGE_NAME)

API_ARTIFACT_IMAGE=$(ARTIFACT_URI)/$(API_DOCKER_IMAGE_NAME):$(TAG)
api_docker_tag_artifact:
	docker tag $(API_DOCKER_IMAGE_NAME):$(TAG) $(API_ARTIFACT_IMAGE)

api_docker_push_artifact:
	docker push $(API_ARTIFACT_IMAGE)
	
api_artifact_push:
	docker tag $(API_DOCKER_IMAGE_NAME):$(TAG) $(API_ARTIFACT_IMAGE)
	docker push $(API_ARTIFACT_IMAGE)

################################ FRONT ################################

FRONT_DOCKER_IMAGE_NAME=front
FRONT_DOCKER_CONTAINER_NAME='container-front'


# test in local
front_local:
	cd front && API_URL='http://localhost:8080' uv run python -m streamlit run app/home.py

# stop the container and remove the image
front_docker_down:
	-docker rm -f $(FRONT_DOCKER_CONTAINER_NAME) 2>/dev/null
	-docker rmi $(FRONT_DOCKER_IMAGE_NAME) 2>/dev/null

# build docker image
front_docker_build: front_docker_down
	@echo Building image "$(FRONT_DOCKER_IMAGE_NAME)"
	docker build --no-cache -f front/Dockerfile -t $(FRONT_DOCKER_IMAGE_NAME) . 

# testing inside the container
front_docker_run_detached: front_docker_down front_docker_build
	-docker rm -f $(FRONT_DOCKER_CONTAINER_NAME) 2>/dev/null
	@echo Running container "$(FRONT_DOCKER_CONTAINER_NAME)"
	docker run -d \
		--name $(FRONT_DOCKER_CONTAINER_NAME) \
		--entrypoint=sh \
		-e API_URL='http://localhost:8080' \
		-p 8502:8502 \
		$(FRONT_DOCKER_IMAGE_NAME) \
		-c "tail -f /dev/null"
	@echo Entering container "$(FRONT_DOCKER_CONTAINER_NAME)"
	docker exec -it $(FRONT_DOCKER_CONTAINER_NAME) sh

# WHEN INSIDE THE CONTAINER, TEST
# tree
# printenv | grep GCP
# ls -l /app/service-account.json
# uv run python -m streamlit run front/app/home.py


# run docker container
front_docker_run: front_docker_build
	-docker rm -f $(FRONT_DOCKER_CONTAINER_NAME) 2>/dev/null
	@echo Running container "$(FRONT_DOCKER_CONTAINER_NAME)"
	docker run -d \
		--name $(FRONT_DOCKER_CONTAINER_NAME) \
		-e API_URL='http://localhost:8080' \
		-p 8502:8502 \
		$(FRONT_DOCKER_IMAGE_NAME)

FRONT_ARTIFACT_IMAGE=$(ARTIFACT_URI)/$(FRONT_DOCKER_IMAGE_NAME):$(TAG)

# retag docker image to artifact syntax + push to artifact repo
# requires steps below
front_artifact_push:
	docker tag $(FRONT_DOCKER_IMAGE_NAME):$(TAG) $(FRONT_ARTIFACT_IMAGE)
	docker push $(FRONT_ARTIFACT_IMAGE)

# Requirements:
# Create Artifact Repository for Docker Images - if it does not exists already
create_artifact_repo:
	gcloud artifacts repositories create $(ARTIFACT_REPO_NAME) \
		--repository-format=docker \
		--location=$(REGION) \
		--description="Docker repository for taxifare FastAPI app"

gcloud_set_artifact_repo:
	gcloud config set artifacts/repository $(ARTIFACT_REPO_NAME)
	gcloud config set artifacts/location $(REGION)

# Authenticate Docker with GCP Artifact Registry - updates docker config ~/.docker/config.json to include auth creds for artifact
authenticate_docker_to_artifact:
	gcloud auth configure-docker $(REGION)-docker.pkg.dev

# rename an existing docker image so it can be pushed to artifact
front_docker_tag_artifact:
	docker tag $(FRONT_DOCKER_IMAGE_NAME):$(TAG) $(FRONT_ARTIFACT_IMAGE)

# Push Docker Image to Artifact Registry
front_docker_push_artifact:
	docker push $(FRONT_ARTIFACT_IMAGE)

############################### RETRAIN ###############################
############################### SCHEDULER #############################
############################### MLFLOW ################################
################################# API #################################
