# frugalAI

## ml pipeline
### Requirements
mlpipeline doit etre run sur un GPU T4

### TODO
-  front 
    - artifact ok 
    - cloud run port ?
- api 
    - artifact
    - vertex (fastapi+transformers)
    - codecarbon

- mlflow

- retrain + scheduler / workflow
    - GPU
    - eval old + retrain + eval new
    - paralleliser
    - codecarbon

- debug / fixes
    - python version 3.11
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
