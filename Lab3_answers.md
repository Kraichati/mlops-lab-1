# Lab 3 — Containerizing the Model with Docker

## Question 1

The model was registered as `food11`, Version 1.
A logged model is saved during a training run, while a
registered model has a shared name and version number,
allowing us to manage different versions of the model.

## Question 2

MLflow replaced fixed stages like `Staging` and `Production` with flexible aliases such as `champion` and `challenger`. Registering models separately from training runs allows independent version management, while aliases can be reassigned to newer versions without changing the application code.

## Question 3

Using an MLflow model URI allows us to load and manage registered model versions without specifying file paths. To serve a newer version, we simply reassign the `champion` alias to it and restart the API to load the updated model.

## Question 4

Copying `pyproject.toml` and `uv.lock` first allows Docker to cache dependency installation. If only `serve.py` changes, Docker reuses the cached dependency layers, making rebuilds faster.

## Question 5

The multi-stage image (`food11-api:latest`) is 3.26GB and the single-stage image (`food11-api:single`) is 3.29GB, so the difference is small. `docker history` shows the biggest layer is the `.venv` copy (6.25GB), which holds torch and the other dependencies. Both images need it, so multi-stage can only save the build tools left behind in the builder stage.

## Question 6

Without `.dockerignore`, Docker sends all those files (data, mlruns, .venv, .git) to the daemon as the build context, so builds become much slower. The final image size doesn't grow unless a `COPY` actually copies them in. The `.venv` folder would be the one that breaks things: it's a Windows environment, and copying it into a Linux image would conflict with the one built inside Docker.

## Question 7

Inside a container, `127.0.0.1` refers to the container itself, not to the host, and MLflow is not running in the container. `host.docker.internal` is a special name that Docker Desktop resolves to the host machine (the Windows PC), so the container can reach the MLflow server running there.

## Question 8

Yes, the new container started from the same image and loaded the model without any rebuild. The image only contains the code and the Python environment. The model itself is not baked in: it is fetched at runtime through the MLflow server and its model files.

## Question 9

The image is only stored on my machine. It needs to be pushed to a container registry (for example Docker Hub) with a version tag so a CI runner or Kubernetes cluster can pull it. The model is also not inside the image: it depends on my local MLflow server and my local `mlruns` folder, so those must be made reachable (for example a shared MLflow server with remote artifact storage) for the container to load the model elsewhere.