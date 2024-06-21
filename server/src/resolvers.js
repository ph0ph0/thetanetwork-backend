const pubsub = require("./pubsub"); // Use the shared pubsub instance
const amqp = require("amqplib");

const rabbitmqUrl = process.env.RABBITMQ_URL || "amqp://localhost";

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

      // Publish task to RabbitMQ queue
      const connection = await amqp.connect(rabbitmqUrl);
      const channel = await connection.createChannel();
      await channel.assertQueue("som_queue", { durable: false });
      console.log("sending task to queue");
      channel.sendToQueue("som_queue", Buffer.from(JSON.stringify(task)));
      console.log(`Task sent to som_queue: ${JSON.stringify(task)}`);

      // Optionally close the connection and channel
      setTimeout(() => {
        channel.close();
        connection.close();
      }, 500);

      // Publish the task to the subscription channel
      pubsub.publish(`TASK_UPDATED_${task.folderPath}`, { taskUpdated: task });

      return task;
    },
  },
};

module.exports = resolvers;
