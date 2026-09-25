# Lab 2 — Model Training and Experiment Tracking with MLflow

## Question 1
After running uv add mlflow torch torchvision scikit-learn, pyproject.toml was updated with the new dependencies, while uv.lock recorded their exact resolved versions and their required dependencies.

## Question 2
`--backend-store-uri` specifies where MLflow stores experiment metadata (parameters, metrics, and run information), while `--default-artifact-root` specifies where artifacts such as trained models are stored. In our project, metadata is stored in `mlflow.db` and artifacts in `mlruns/`.

## Question 3
`mlflow.db` and `mlruns/` should not be tracked by Git or DVC because they are local experiment outputs already managed by MLflow, can become large, and change frequently during training.


## Question 4
The first time `mlflow.set_experiment("food11")` is called, MLflow automatically creates the experiment if it does not exist and uses it to organize subsequent training runs.

## Question 5
`mlflow.log_param` records fixed hyperparameters, while `mlflow.log_metric` records training results; metrics use `step` to track their evolution across epochs, whereas parameters remain fixed throughout the run.

## Question 6
The parameters, metric charts, and logged model can be viewed in the MLflow UI. The trained ResNet18 model is stored locally under `mlruns/1/models/<model-id>/artifacts/data/model.pth`.

## Question 7
The learning rate of 0.0001 achieved the highest validation accuracy (70.89%). A higher learning rate is not always better, as it can cause unstable optimization and reduce model performance.

## Question 8
The parallel coordinates plot shows that smaller learning rates produced higher validation accuracy, while increasing the batch size from 32 to 64 at a learning rate of 0.001 also improved accuracy in our experiments.

## Question 9
The run `zealous-skink-337` achieved the highest final validation accuracy of 70.89%.
Run ID: a386e81610ce46eab6b648c885970f4c