const amqp = require("amqplib");

const logger = console;

class ValModConsumer {
  constructor() {
    this.shouldReconnect = false;
    this.wasConsuming = false;
    this.connection = null;
    this.channel = null;
    this.closing = false;
    this.consuming = false;
    this.url = "amqp://guest:guest@34.231.140.237";
  }

  async connect() {
    logger.info(`Connecting to ${this.url}`);
    return await amqp.connect(this.url);
  }

  async onConnectionOpen(connection) {
    logger.info("Connection opened");
    this.connection = connection;
    await this.openChannel();
  }

  async onConnectionOpenError(err) {
    logger.error(`Connection open failed: ${err}`);
    await this.reconnect();
  }

  async onConnectionClosed(reason) {
    this.channel = null;
    if (this.closing) {
      this.connection = null;
    } else {
      logger.warning(`Connection closed, reconnect necessary: ${reason}`);
      await this.reconnect();
    }
  }

  async reconnect() {
    this.shouldReconnect = true;
    await this.stop();
  }

  async openChannel() {
    logger.info("Creating a new channel");
    this.channel = await this.connection.createChannel();
    logger.info("Channel opened");
    await this.setupQueue("val_queue");
  }

  async setupQueue(queueName) {
    logger.info(`Declaring queue ${queueName}`);
    const queue = await this.channel.assertQueue(queueName, { durable: false });
    await this.startConsuming(queue);
  }

  async startConsuming(queue) {
    logger.info("Issuing consumer related RPC commands");
    await this.channel.consume(queue.queue, async (message) => {
      if (message !== null) {
        await this.onMessage(message);
        this.channel.ack(message);
      }
    });
  }

  async onMessage(message) {
    logger.info(
      `Received message # ${
        message.fields.deliveryTag
      }: ${message.content.toString()}`
    );
    await this.processMessage(message.content);
  }

  async processMessage(body) {
    const data = JSON.parse(body);
    const processedData = await this.processDataWithModel(data);
    logger.info(`Processed data: ${JSON.stringify(processedData)}`);
    await this.addToUpdateTaskQueue(processedData);
    logger.info(
      `Added data to update_task_queue: ${JSON.stringify(processedData)}`
    );
  }

  async processDataWithModel(data) {
    await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulating processing time
    return data;
  }

  async addToUpdateTaskQueue(data) {
    await this.channel.assertQueue("update_task_queue", { durable: false });
    await this.channel.sendToQueue(
      "update_task_queue",
      Buffer.from(JSON.stringify(data))
    );
  }

  async stopConsuming() {
    if (this.channel) {
      logger.info("Stopping consuming");
      await this.channel.close();
    }
  }

  async runAsync() {
    while (!this.closing) {
      try {
        this.connection = await this.connect();
        await this.onConnectionOpen(this.connection);
        this.consuming = true;
        while (this.consuming) {
          await new Promise((resolve) => setTimeout(resolve, 100));
        }
      } catch (err) {
        logger.error(`Error: ${err}`);
        await new Promise((resolve) => setTimeout(resolve, 5000));
      } finally {
        await this.stop();
      }
    }
  }

  async stop() {
    if (!this.closing) {
      this.closing = true;
      logger.info("Stopping");
      if (this.consuming) {
        await this.stopConsuming();
      }
      if (this.connection) {
        await this.connection.close();
      }
      logger.info("Stopped");
    }
  }
}

module.exports = ValModConsumer;
