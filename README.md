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

Push build to docker
```
docker push <username>/<your-repo>:<your-tag>
```

Run remote docker image
```
docker run -d -p <port>:<port> <username>/<your-repo>:<your-tag>
```
