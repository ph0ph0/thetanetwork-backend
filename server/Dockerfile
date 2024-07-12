FROM node:18

# Create app directory
WORKDIR /usr/src/app

# Install app dependencies
COPY package*.json ./
RUN npm install

# Bundle app source
COPY . .

ENV RABBITMQ_URL=amqp://guest:guest@44.209.101.218

# Expose the port the app runs on
EXPOSE 4000

# Command to run the app
CMD [ "node", "src/index.js" ]
