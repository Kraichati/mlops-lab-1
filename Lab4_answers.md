# Lab 4 - Orchestrating the app with Docker Compose

## Question 1

Everything written to `/mlflow-data` is stored in the container's own writable layer. When the container is removed, that layer is deleted, so the new container started empty: the experiment I created was gone and only "Default" remained.

## Question 2

A named volume is managed by Docker, so it does not depend on a path that exists on the host machine, and it works the same on Windows, Mac and Linux. It also avoids file permission and path problems, and it keeps the database and artifacts out of the git repo. A bind mount could also work and would persist the data, but it ties the setup to a specific folder on my machine, and on Windows it can cause permission and performance problems with SQLite. A named volume is the portable and cleaner choice.

## Question 3

Compose creates a private network for the services and runs a built-in DNS on it. Each service name (like `mlflow`) resolves to that container's IP. In Lab 3 the container was on Docker's default network and had no name for my host, so `127.0.0.1` pointed to the container itself and I needed `host.docker.internal` or `--network host`.

## Question 4

Reading `INFERENCE_URL` from an environment variable keeps the image reusable. The name `inference` only exists inside the Compose network. If I ran this image alone with `docker run`, the hardcoded name would not resolve and the app would fail. With an environment variable I can set the right address for each situation without rebuilding the image.

## Question 5

Service-to-service traffic stays inside the Compose network, so `inference` does not need a published port. The frontend reaches it by service name (`http://inference:8000`), which Compose's DNS resolves to the container. Only `mlflow` and `frontend` publish ports because a human needs to reach them from the browser.

## Question 6

`depends_on` only waits for the mlflow container to start, not for the server inside it to be ready. If `serve.py` tries to load the model before mlflow accepts connections, the load fails, startup fails, and the `inference` container exits with an error. `docker compose logs inference` would show the connection error.

## Question 7

`docker compose ps` lists published ports for `mlflow` (5000) and `frontend` (8501), but `inference` only shows its internal port 8000 with no mapping to the host. This matches the `docker-compose.yml`: only the services a human needs to open in the browser publish a port, and inference is reached by the frontend through the Compose network.

## Question 8

The prediction came from the old model version. After I moved the `champion` alias to the new version, the frontend still returned the same result (Egg, 57.7%), because `serve.py` loads the model once at startup and the running container kept the old version in memory. The command that picks up the new version without rebuilding any image is `docker compose restart inference`. After it, the same image gave a different prediction (Bread, 46.9%).

## Question 9

`restart` is enough because the model is not baked into the inference image. The image only contains the code and the Python environment. At startup the container asks MLflow for the version behind the `champion` alias and downloads the model files from the MLflow server (the logs show the artifact download on each start), so restarting the container fetches the new version.

## Question 10

After `docker compose down` followed by `docker compose up`, the registered model and its `champion` alias were still there, along with the experiments and runs. `down` removes the containers and the network but keeps the named volume, and the MLflow database and artifacts live on that volume.

## Question 11

Docker Compose runs everything on a single machine, so it cannot give us several things. To run `inference` as three replicas behind a load balancer, I would need an orchestrator such as Kubernetes (or Docker Swarm), which can start multiple copies, spread them across machines, and put a load balancer or Service in front of them, with health checks and rolling updates. For the mlflow service to survive a machine failure, I would need to run it across more than one machine and replace the local SQLite file and the local volume with shared, durable storage, for example a database server such as PostgreSQL and remote artifact storage such as S3. Compose also cannot restart a service on another machine when its host fails, because everything depends on that one host.

## Notes

- `src/food11/train.py`: the experiment name was changed from `food11` to `food11-v2`, so that runs created after enabling `--serve-artifacts` on the containerized MLflow server use a `mlflow-artifacts:/` location the inference container can download from.
- `mlflow/Dockerfile`: I added `--allowed-hosts` (the server rejected the host name `mlflow:5000` with a 403) and replaced `--default-artifact-root` with `--artifacts-destination` plus `--serve-artifacts` (the inference container could not read a path inside the MLflow container).