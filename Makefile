# include .env
ifneq (,$(wildcard .env))
  include .env
  export
endif


.PHONY: streamlit api up

PATH_SERVICE_ACCOUNT_KEY=frugalai-2025-080c1bf50146.json

# Artifact
ARTIFACT_REPOSITORY=frugalai-repo
ARTIFACT_URI = $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT_ID)/$(ARTIFACT_REPOSITORY)
TAG=latest

# Cloud SQL
INSTANCE_NAME=mlflow-backend-store-replica
DB_NAME=mlflow_backend
DB_USER=mlflow_user
DB_PASSWORD=frugalai
PUBLIC_IP=34.105.180.151
DB_PORT=5432

########## RULES TO DEPLOY ##########
# mlflow_deploy
# front_deploy



########## Create storage ressources ##########
# Bucket : Mlflow artifact store + models bucket
# create_bucket:
# 	gsutil cp -r gs://frugalai-models/* gs://$(GCS_BUCKET_NAME)
# 	gsutil cp -r gs://frugalai-mlflow-artifacts/* gs://frugalai-mlflow-artifacts-w2/
# gsutil mb -p $(GCP_PROJECT_ID) -l $(GCP_REGION) -c standard gs://$(GCS_BUCKET_NAME)
# gsutil mb -p $(GCP_PROJECT_ID) -l $(GCP_REGION) -c standard gs://$(GCS_MLFLOW_BUCKET_NAME)

# CloudSQL : Mlflow backend
create_sql_replica:
	gcloud sql instances create $(INSTANCE_NAME) \
	--master-instance-name=mlflow-backend-store \
	--region=$(GCP_REGION)
	gcloud sql instances promote-replica $(INSTANCE_NAME)

# Feedback Big query
create_bq:
	bq mk \
	--dataset \
	--location=$(GCP_REGION) \
	$(BQ_DATASET_ID)_w2
	bq show --schema --format=prettyjson $(BQ_DATASET_ID).$(BQ_TABLE_ID) > schema.json
	bq mk --table \
	--schema=schema.json \
	$(BQ_DATASET_ID)_w2.$(BQ_TABLE_ID)

# Artifact registry for docker images : front, api, mlflow-tracking
create_artifact_repo:
	gcloud artifacts repositories create $(ARTIFACT_REPOSITORY) \
		--repository-format=docker \
		--location=$(GCP_REGION) \
		--description="Docker repository"

gcloud_set_artifact_repo:
	gcloud config set artifacts/repository $(ARTIFACT_REPOSITORY)
	gcloud config set artifacts/location $(GCP_REGION)

# Authenticate Docker with GCP Artifact Registry - updates docker config ~/.docker/config.json to include auth creds for artifact
authenticate_docker_to_artifact:
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev




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
API_PORT=8080
API_ARTIFACT_IMAGE=$(ARTIFACT_URI)/$(API_DOCKER_IMAGE_NAME):$(TAG)

PROD_MODEL_NAME=frugalai-api


# test in local
api_local:
	UV_ENV_FILE=".env" && cd api && uv run uvicorn app.main:app --host 0.0.0.0 --port $(API_PORT) --reload

# stop the container and remove the image
api_docker_down:
	-docker rm -f $(API_DOCKER_CONTAINER_NAME) 2>/dev/null
	-docker rmi $(API_DOCKER_IMAGE_NAME) 2>/dev/null

# build docker image
api_docker_build: api_docker_down
	@echo Building image "$(API_DOCKER_IMAGE_NAME)"
	docker build --no-cache -f api/Dockerfile -t $(API_DOCKER_IMAGE_NAME) . 

api_docker_build_artifact: api_docker_down
	@echo Building image "$(API_DOCKER_IMAGE_NAME)"
	docker build --platform linux/amd64 --no-cache -f api/Dockerfile -t $(API_DOCKER_IMAGE_NAME) . 

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
		-p $(API_PORT):$(API_PORT) \
		$(API_DOCKER_IMAGE_NAME) \
		-c "tail -f /dev/null"
	@echo Entering container "$(API_DOCKER_CONTAINER_NAME)"
	docker exec -it $(API_DOCKER_CONTAINER_NAME) sh

# WHEN INSIDE THE CONTAINER, TEST
# tree
# printenv | grep GCP
# ls -l /app/service-account.json
# uvicorn api.app.main:app --host 0.0.0.0 --port $(API_PORT)


# run docker container
api_docker_run: api_docker_build
	-docker rm -f $(API_DOCKER_CONTAINER_NAME) 2>/dev/null
	@echo Running container "$(API_DOCKER_CONTAINER_NAME)"
	docker run -d \
		--name $(API_DOCKER_CONTAINER_NAME) \
		--env-file .env \
		-e GOOGLE_APPLICATION_CREDENTIALS='/app/service-account.json' \
		-v $(shell pwd)/$(PATH_SERVICE_ACCOUNT_KEY):/app/service-account.json \
		-p $(API_PORT):$(API_PORT) \
		$(API_DOCKER_IMAGE_NAME)

api_tag_artifact:
	docker tag $(API_DOCKER_IMAGE_NAME):$(TAG) $(API_ARTIFACT_IMAGE)

api_push_artifact:
	docker push $(API_ARTIFACT_IMAGE)
	
api_tag_push: api_tag_artifact api_push_artifact
	@echo Pushing image "$(API_ARTIFACT_IMAGE)" to google artifact registry

# roles/aiplatform.admin
# roles/artifactregistry.reader
# roles/storage.objectViewer
api_upload_container_vertex: api_docker_build_artifact api_tag_push
	gcloud ai models upload \
	--project=$(GCP_PROJECT_ID) \
	--region=$(GCP_REGION) \
	--display-name=$(PROD_MODEL_NAME) \
	--container-image-uri=$(API_ARTIFACT_IMAGE) \
	--container-health-route=/health \
	--container-predict-route=/predict \
	--container-env-vars="$(grep -v '^#' .env | xargs | sed 's/ /,/g')" \
	--container-port=$(API_PORT) \
	--service-account=api-sa@frugalai-2025.iam.gserviceaccount.com

api_create_endpoint_vertex:
	gcloud ai endpoints create \
	--region=$(GCP_REGION) \
	--display-name=$(PROD_MODEL_NAME)-endpoint

api_which_endpoin_id:
	gcloud ai endpoints list \
	--region=$(GCP_REGION) \
	--filter="displayName=$(PROD_MODEL_NAME)-endpoint" \
	--format="value(name)"

ENDPOINT_ID=5074127414930440192

api_which_model_id:
	gcloud ai models list \
	--region=$(GCP_REGION) \
	--filter="displayName=$(PROD_MODEL_NAME)" \
	--format="value(name)"

MODEL_ID=956755436072075264

api_deploy_endpoint:
	gcloud ai endpoints deploy-model $(ENDPOINT_ID) \
	--region=$(GCP_REGION) \
	--model=$(MODEL_ID) \
	--display-name=$(PROD_MODEL_NAME)-deployment \
	--machine-type=n1-standard-4 \
	--accelerator=type=nvidia-tesla-t4,count=1 \
	--traffic-split=0=100 \
	--service-account=api-sa@frugalai-2025.iam.gserviceaccount.com \
	--enable-access-logging

api_test_endpoint: 
	gcloud ai endpoints predict $(ENDPOINT_ID) \
	--region=$(GCP_REGION) \
	--json-request=<(echo '{"instances": [{"user_claim": "Climate change is very nice."}]}')

# api_deploy_cleanup:
# 	gcloud ai models list --region=$(GCP_REGION)
# 	gcloud ai models delete <model-id> --region=$(GCP_REGION)


api_SA_create:
	gcloud iam service-accounts create api-sa \   
    --display-name="API Service Account" 

SA_list:
	gcloud iam service-accounts list 

# roles/bigquery.dataEditor
# roles/run.invoker
api_SA_add_iam:
	gcloud projects add-iam-policy-binding frugalai-2025 \
	--member="serviceAccount:api-sa@frugalai-2025.iam.gserviceaccount.com" \
	--role="roles/bigquery.dataEditor"
	gcloud projects add-iam-policy-binding frugalai-2025 \
	--member="serviceAccount:api-sa@frugalai-2025.iam.gserviceaccount.com" \
	--role="roles/run.invoker"


################################ FRONT ################################

FRONT_DOCKER_IMAGE_NAME=front
FRONT_DOCKER_CONTAINER_NAME='container-front'
FRONT_PORT=8502
FRONT_ARTIFACT_IMAGE=$(ARTIFACT_URI)/$(FRONT_DOCKER_IMAGE_NAME):$(TAG)


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

front_docker_build_artifact: front_docker_down
	@echo Building image "$(FRONT_DOCKER_IMAGE_NAME)"
	docker build --platform linux/amd64 --no-cache -f front/Dockerfile -t $(FRONT_DOCKER_IMAGE_NAME) . 

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
		-e PORT=$(FRONT_PORT) \
		-p $(FRONT_PORT):$(FRONT_PORT) \
		$(FRONT_DOCKER_IMAGE_NAME)


# Requirements:
# rename an existing docker image so it can be pushed to artifact
front_tag_artifact:
	docker tag $(FRONT_DOCKER_IMAGE_NAME):$(TAG) $(FRONT_ARTIFACT_IMAGE)

# Push Docker Image to Artifact Registry
front_push_artifact:
	docker push $(FRONT_ARTIFACT_IMAGE)

# retag docker image to artifact syntax + push to artifact repo
# requires steps below
front_tag_push: front_tag_artifact front_push_artifact
	@echo Pushing image "$(FRONT_ARTIFACT_IMAGE)" to google artifact registry

# roles/run.invoker

front_deploy: front_docker_build_artifact front_tag_push
	gcloud run deploy $(FRONT_DOCKER_IMAGE_NAME) \
	--image=$(FRONT_ARTIFACT_IMAGE) \
	--region=$(GCP_REGION) \
	--platform=managed \
	--allow-unauthenticated \
	--set-env-vars API_URL='http://localhost:8080' \
	--service-account front-sa@frugalai-2025.iam.gserviceaccount.com \
	--port=$(FRONT_PORT)

############################### RETRAIN ###############################
############################### SCHEDULER #############################
############################### MLFLOW ################################

MLFLOW_DOCKER_IMAGE_NAME=mlflow
MLFLOW_DOCKER_CONTAINER_NAME='container-mlflow'
MLFLOW_PORT=5000

MLFLOW_ARTIFACT_IMAGE=$(ARTIFACT_URI)/$(MLFLOW_DOCKER_IMAGE_NAME):$(TAG)
BACKEND_STORE_URI=postgresql+psycopg2://$(DB_USER):$(DB_PASSWORD)@$(PUBLIC_IP):$(DB_PORT)/$(DB_NAME)
GCS_MLFLOW_BUCKET_NAME=frugalai-mlflow-artifacts-w2



# test in local
mlflow_local:
	echo Starting mlflow server
	cd mlflow-tracking && uv run mlflow server \
	--backend-store-uri $(BACKEND_STORE_URI) \
	--default-artifact-root gs://$(GCS_MLFLOW_BUCKET_NAME) \
	--host 0.0.0.0 \
	--port $(MLFLOW_PORT)

connexion_test:
	docker run -it --rm postgres:15 \
	psql -h $(PUBLIC_IP) -U $(DB_USER) -d $(DB_NAME)

# stop the container and remove the image
mlflow_docker_down:
	-docker rm -f $(MLFLOW_DOCKER_CONTAINER_NAME) 2>/dev/null
	-docker rmi $(MLFLOW_DOCKER_IMAGE_NAME) 2>/dev/null

# build docker image
# Architecture Mismatch : from (ARM64/Apple Silicon) to (AMD64/x86_64) -> add --platform linux/amd64
mlflow_docker_build: mlflow_docker_down
	@echo Building image "$(MLFLOW_DOCKER_IMAGE_NAME)"
	docker build --no-cache -f mlflow-tracking/Dockerfile -t $(MLFLOW_DOCKER_IMAGE_NAME) . 

mlflow_docker_build_artifact: mlflow_docker_down
	@echo Building image "$(MLFLOW_DOCKER_IMAGE_NAME)"
	docker build --platform linux/amd64 --no-cache -f mlflow-tracking/Dockerfile -t $(MLFLOW_DOCKER_IMAGE_NAME) . 

# run container, overwrites PORT and GOOGLE_APPLICATION_CREDENTIALS
mlflow_docker_run: mlflow_docker_build
	-docker rm -f $(MLFLOW_DOCKER_CONTAINER_NAME) 2>/dev/null
	@echo Running container "$(MLFLOW_DOCKER_CONTAINER_NAME)"
	docker run -d \
		--name $(MLFLOW_DOCKER_CONTAINER_NAME) \
		--env-file .env \
		-e GOOGLE_APPLICATION_CREDENTIALS='/app/service-account.json' \
		-e ARTIFACT_ROOT=gs://$(GCS_MLFLOW_BUCKET_NAME) \
		-e BACKEND_STORE_URI=$(BACKEND_STORE_URI) \
		-e PORT=$(MLFLOW_PORT) \
		-v $(shell pwd)/$(PATH_SERVICE_ACCOUNT_KEY):/app/service-account.json \
		-p $(MLFLOW_PORT):$(MLFLOW_PORT) \
		$(MLFLOW_DOCKER_IMAGE_NAME) 

mlflow_tag_artifact:
	docker tag $(MLFLOW_DOCKER_IMAGE_NAME):$(TAG) $(MLFLOW_ARTIFACT_IMAGE)

mlflow_push_artifact:
	docker push $(MLFLOW_ARTIFACT_IMAGE)
	
mlflow_tag_push: mlflow_tag_artifact mlflow_push_artifact
	@echo Pushing image "$(MLFLOW_ARTIFACT_IMAGE)" to google artifact registry

# Memory limit of 512 MiB exceeded, need to have 1G
# consider taking out the port value
mlflow_deploy: mlflow_docker_build_artifact mlflow_tag_push
	gcloud run deploy $(MLFLOW_DOCKER_IMAGE_NAME) \
	--image=$(MLFLOW_ARTIFACT_IMAGE) \
	--region=$(GCP_REGION) \
	--platform=managed \
	--allow-unauthenticated \
	--memory=1Gi \
	--set-env-vars ARTIFACT_ROOT=gs://$(GCS_MLFLOW_BUCKET_NAME) \
	--set-env-vars BACKEND_STORE_URI=$(BACKEND_STORE_URI) \
	--service-account mlflow-executor@frugalai-2025.iam.gserviceaccount.com
	--port=8080

### Handling IAM and permissions
mlflow_SA_create:
	gcloud iam service-accounts create mlflow-executor \
	--display-name "Service Account for MLflow on Cloud Run"

mlflow_SA_list:
	gcloud iam service-accounts list 

# roles/cloudsql.client
# roles/storage.admin
# storage.objectAdmin
mlflow_SA_add_iam:
	gcloud projects add-iam-policy-binding frugalai-2025 \
	--member="serviceAccount:mlflow-executor@frugalai-2025.iam.gserviceaccount.com" \
	--role="roles/storage.objectAdmin"
	gcloud projects add-iam-policy-binding frugalai-2025 \
	--member="serviceAccount:mlflow-executor@frugalai-2025.iam.gserviceaccount.com" \
	--role="roles/cloudsql.client"


mlflow_SA_check_iam:
	gcloud projects get-iam-policy frugalai-2025 \        
	--flatten="bindings[].members" \
	--format="table(bindings.role)" \
	--filter="bindings.members:mlflow-executor@frugalai-2025.iam.gserviceaccount.com"

mlflow_bucket_check_iam:
	gsutil iam get gs://frugalai-mlflow-artifacts
	
mlflow_bucket_add_iam:
	gsutil iam ch serviceAccount:mlflow-executor@frugalai-2025.iam.gserviceaccount.com:objectAdmin gs://frugalai-mlflow-artifacts

################################# API #################################
