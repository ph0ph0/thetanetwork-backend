const amqp = require("amqplib");
const pubsub = require("./pubsub");

const rabbitmqUrl = process.env.RABBITMQ_URL || "amqp://localhost";

let connection, channel;

const initRabbitMQ = async () => {
  try {
    connection = await amqp.connect(rabbitmqUrl);
    channel = await connection.createChannel();
    await channel.assertQueue("val_queue", { durable: false });

    connection.on("error", (err) => {
      console.error("RabbitMQ connection error", err);
      setTimeout(initRabbitMQ, 5000);
    });

    connection.on("close", () => {
      console.error("RabbitMQ connection closed");
      setTimeout(initRabbitMQ, 5000);
    });

    channel.on("error", (err) => {
      console.error("RabbitMQ channel error", err);
      setTimeout(initRabbitMQ, 5000);
    });

    channel.on("close", () => {
      console.error("RabbitMQ channel closed");
      setTimeout(initRabbitMQ, 5000);
    });

    console.log("Connected to RabbitMQ");
  } catch (error) {
    console.error("Failed to connect to RabbitMQ:", error);
    setTimeout(initRabbitMQ, 5000);
  }
};

initRabbitMQ();

const resolvers = {
  Subscription: {
    taskUpdated: {
      subscribe: (_, { folderPath }) => {
        return pubsub.asyncIterator(`TASK_UPDATED_${folderPath}`);
      },
    },
  },
  Mutation: {
    createTask: async (_, { input }) => {
      const task = { ...input, status: "Pending", valuation: 0 };
      console.log(`Task created: ${JSON.stringify(task)}`);

      try {
        if (!channel || channel.closed) {
          await initRabbitMQ();
        }

        console.log("Sending task to queue");
        await channel.sendToQueue(
          "val_queue",
          Buffer.from(JSON.stringify(task))
        );
        console.log(`Task sent to val_queue: ${JSON.stringify(task)}`);

        // Publish the task to the subscription channel
        pubsub.publish(`TASK_UPDATED_${task.folderPath}`, {
          taskUpdated: task,
        });

        return task;
      } catch (error) {
        console.error("Error in createTask:", error);
        throw new Error("Failed to create task");
      }
    },
  },
};

module.exports = resolvers;
