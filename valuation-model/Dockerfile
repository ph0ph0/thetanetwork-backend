# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y git

# Copy the current directory contents into the container at /usr/src/app
COPY . .

ENV RABBITMQ_URL=amqp://guest:guest@34.231.140.237

# Update pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entrypoint script
COPY entrypoint.sh /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the entrypoint script
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
