# Use an official Node.js runtime as a parent image
FROM node:18

# Set the working directory in the container
WORKDIR /usr/src/app

# TODO Uncomment
# Install system dependencies
# RUN apt-get update && apt-get install -y git

# Copy package.json and package-lock.json
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

# Copy the current directory contents into the container at /usr/src/app
COPY . .

ENV RABBITMQ_URL=amqp://guest:guest@34.231.140.237

# TODO Uncomment
# Copy the entrypoint script
# COPY entrypoint.sh /usr/src/app/entrypoint.sh
# RUN chmod +x /usr/src/app/entrypoint.sh

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Command to run the app
CMD [ "node", "src/index.js" ]

# TODO Uncomment
# Run the entrypoint script
# ENTRYPOINT ["/usr/src/app/entrypoint.sh"]