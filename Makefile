.PHONY: streamlit api up

# stop all containers
docker_stop:
	@docker ps -q | xargs -r docker stop

# clean all ressources
docker_cleanup:
	@docker ps -q | xargs -r docker stop
	@docker ps -aq | xargs -r docker rm
	@docker system prune -f


################################ FRONT ################################


front_local:
	$(MAKE) -C front streamlit-dev


################################# API #################################

DOCKER_IMAGE_NAME=api
DOCKER_CONTAINER_NAME='container-api'
PATH_SERVICE_ACCOUNT_KEY=frugalai-2025-080c1bf50146.json

# test in local
api_local:
	UV_ENV_FILE=".env" uv run uvicorn api.app.main:app --host 0.0.0.0 --port 8080 --reload

# build docker image
api_docker_build:
	@echo Building image "$(DOCKER_IMAGE_NAME)"
	@docker build --no-cache -f api/Dockerfile -t $(DOCKER_IMAGE_NAME) . 

# testing inside the container
api_docker_run_detached: docker_cleanup api_local_docker_build
	@-docker rm -f $(DOCKER_CONTAINER_NAME) 2>/dev/null
	@echo Running container "$(DOCKER_CONTAINER_NAME)"
	@docker run -d \
		--name $(DOCKER_CONTAINER_NAME) \
		--env-file .env \
		-m 12g \
		-e GOOGLE_APPLICATION_CREDENTIALS='/app/service-account.json' \
		-v $(shell pwd)/$(PATH_SERVICE_ACCOUNT_KEY):/app/service-account.json \
		--entrypoint=sh \
		-p 8080:8080 \
		$(DOCKER_IMAGE_NAME) \
		-c "tail -f /dev/null"
	@echo Entering container "$(DOCKER_CONTAINER_NAME)"
	@docker exec -it $(DOCKER_CONTAINER_NAME) sh

# DEBUG
# tree
# printenv | grep GCP
# ls -l /app/service-account.json
# uvicorn api.app.main:app --host 0.0.0.0 --port 8080


# run docker container
api_docker_run: docker_cleanup api_local_docker_build
	@echo Running container "$(DOCKER_CONTAINER_NAME)"
	@docker run -d \
		--name $(DOCKER_CONTAINER_NAME) \
		--env-file .env \
		-e GOOGLE_APPLICATION_CREDENTIALS='/app/service-account.json' \
		-v $(shell pwd)/$(PATH_SERVICE_ACCOUNT_KEY):/app/service-account.json \
		-p 8080:8080 \
		$(DOCKER_IMAGE_NAME)


############################### RETRAIN ###############################
############################### SCHEDULER #############################
############################### MLFLOW ################################
################################# API #################################
