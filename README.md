# frugalAI

## ml pipeline
### Requirements
mlpipeline doit etre run sur un GPU T4

### TODO
-  front 
https://front-1002353787705.europe-west9.run.app/
    - artifact ok 
    - cloud run port ? ok
- api 
    - artifact - ok
    - vertex (fastapi+transformers) - WIP
        - update docker to make it vertex compatible

- mlflow
https://mlflow-1002353787705.europe-west9.run.app/
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
    - GPU
    - eval old + retrain + eval new
    - paralleliser

- debug / fixes
    - python version 3.12.11
    - docker images dynamic PORT
    - simplifier image + multiphase pour alleger

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
- terraform import project

bonus
- model package
    - train from scratch
    - other models - ML, DL comparaison
- dashboard - comparaison
- vllm instead of fastapi + transformers
