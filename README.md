# frugalAI

## ml pipeline
### Requirements
mlpipeline doit etre run sur un GPU T4

### TODO
-  front 
    - artifact ok 
    - cloud run port ? WIP
- api 
    - artifact - ok
    - vertex (fastapi+transformers) - WIP

- mlflow
    - local tracking server with remote ressources ok
    - use mlflow_track into code and test - ok
    - include codecarbon - ok
    - dockerize and test - ok
    - push to artifact - ok
    - deploy to cloud run - ok
    - integration test from local WIP
    - set up VPC network

    - simplifier image
    - use mlflow log and load model and test (when retrain)

- retrain + scheduler / workflow
    - GPU
    - eval old + retrain + eval new
    - paralleliser

- debug / fixes
    - python version 3.12.11
    - docker images dynamic PORT

- testing

- optimization 
    - model (distillation, pruna, quantisation)
    - api (cached model, trigger reload)
    - front (cache requests/response)
    - scheduler (daily check, triggers reload if enough feedback, update flag retrained)
    - (vllm (options, batch))
    - cloud options (location, voir pour chaque produit, comparaison produits)
    - docker (diminuer la taille de l'image)

- CICD
    - test
    - build - matrix build if changes or use paths
    - push
- logging
- monitoring
- langfuse

bonus
- model package
    - train from scratch
    - other models - ML, DL comparaison
- dashboard - comparaison
- vllm instead of fastapi + transformers
