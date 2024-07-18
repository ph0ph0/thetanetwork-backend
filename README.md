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

## Setup UI

```
sudo nano /etc/rabbitmq/rabbitmq.conf
```

Add to file and save:
```
loopback_users.guest = false
listeners.tcp.default = 5672
management.listener.port = 15672
```
Restart rMQ in ubuntu user folder:
```
sudo systemctl restart rabbitmq-server
```
Go to IP/15672/ (eg http://34.231.140.237:15672/#/)
Login with guest guest

# Stop and remove rMQ
```
sudo systemctl stop rabbitmq-server -y
sudo apt-get remove --purge rabbitmq-server -y
sudo apt-get autoremove -y
sudo rm -rf /var/lib/rabbitmq/
sudo rm -rf /etc/rabbitmq/
sudo rm -rf /var/lib/rabbitmq/mnesia
```
Reinstall and setup after removing

Complete stop and restart steps before setting config:
```
sudo systemctl stop rabbitmq-server -y
sudo apt-get remove --purge rabbitmq-server -y
sudo apt-get autoremove -y
sudo rm -rf /var/lib/rabbitmq/
sudo rm -rf /etc/rabbitmq/
sudo rm -rf /var/lib/rabbitmq/mnesia
sudo apt update
sudo apt install rabbitmq-server -y
sudo systemctl start rabbitmq-server
sudo rabbitmq-plugins enable rabbitmq_management
sudo systemctl enable rabbitmq-server