# frugalAI

## ml pipeline
### Requirements
mlpipeline doit etre run sur un GPU T4

### TODO
    - python version 3.12.11
    - simplifier image + multiphase pour alleger

1. deploy api
2. link to front
3. integration test - front/api/mlflow/bq/cloudsql/bucketmodels
4. CICD
5. optimisation
5. retrain

- api 
    - links : creation BQ + iam BQ + iam Mflow
    - artifact - ok
    - vertex (fastapi+transformers) - WIP
        - update docker to make it vertex compatible - ok

https://front-1002353787705.europe-west2.run.app
-  front 
    - links : iam api
    - artifact ok 
    - cloud run port ? ok
    - mettre a jour l'adresse de l'endpoint

https://mlflow-1002353787705.europe-west2.run.app
- mlflow
    - links : Cloud SQL + iam + GCS Bucket + iam
    - local tracking server with remote ressources ok
    - use mlflow_track into code and test - ok
    - include codecarbon - ok
    - dockerize and test - ok
    - push to artifact - ok
    - deploy to cloud run - ok
    - integration test from local ok
    - use mlflow log and load model and test ok

    - test with LLMs, test retrain
    - set up VPC network

- retrain + scheduler / workflow
    - links : iam mlflow, iam BQ
    - GPU
    - eval old + retrain + eval new
    - paralleliser

- CICD
    - test
    - build - matrix build if changes or use paths
    - push

- bonus
    - logging
    - monitoring prometheus + grafana
    - langfuse
    - terraform import project

- debug / fixes

- optimization 
    - model (distillation, pruna, quantisation)
    - ok api (cached model, trigger reload)
    - ok front (cache requests/response)
    - scheduler (daily check, triggers reload if enough feedback, update flag retrained)
    - (vllm (options, batch))
    - ok cloud options (location, voir pour chaque produit, comparaison produits)
    - ok docker (diminuer la taille de l'image)




bonus++
- model package
    - train from scratch
    - other models - ML, DL comparaison
- dashboard - comparaison
- vllm instead of fastapi + transformers
