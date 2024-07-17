Build all containers from root
```
docker-compose up --build
```

Build individual containers from each folder
```
docker build -t <name> .
```

Run individual container
```
docker run -p <port>:<port> <name>
```

Build before pushing to docker
```
docker build -t <username>/<name>:latest .
```

Push build to docker
```
docker push <username>/<your-repo>:<your-tag>
```

Run remote docker image
```
docker run -d -p <port>:<port> <username>/<your-repo>:<your-tag>
```

# RabbitMQ

If queue requires multiple requests to complete a full cycle, restart the server.

## Installation
```
sudo apt update
sudo apt install rabbitmq-server -y
```

## Run

```
sudo systemctl start rabbitmq-server
sudo rabbitmq-plugins enable rabbitmq_management
sudo systemctl enable rabbitmq-server
```

## Status

```
sudo systemctl status rabbitmq-server
```