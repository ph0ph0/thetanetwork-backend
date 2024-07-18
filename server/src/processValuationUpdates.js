const amqp = require("amqplib");
const pubsub = require("./pubsub");

let connection, channel;

async function initRabbitMQ() {
  try {
    const rabbitmqUrl = process.env.RABBITMQ_URL || "amqp://rabbitmq";
    connection = await amqp.connect(rabbitmqUrl);
    channel = await connection.createChannel();
    await channel.assertQueue("update_task_queue", { durable: false });

    console.log("Connected to RabbitMQ, waiting for messages");

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

    channel.consume("update_task_queue", (msg) => {
      if (msg !== null) {
        console.log("Received message from server queue");
        const { valuation, walletAddress, folderPath, id, desc, status } =
          JSON.parse(msg.content.toString());

        let task = { valuation, walletAddress, folderPath, id, desc, status };
        task.valuation = valuation;
        task.status = "Completed";

        console.log(`Finished, task updated: ${JSON.stringify(task)}`);
        pubsub.publish(`TASK_UPDATED_${folderPath}`, { taskUpdated: task });

        channel.ack(msg);
      }
    });
  } catch (error) {
    console.error("Error in initRabbitMQ:", error);
    setTimeout(initRabbitMQ, 5000);
  }
}

async function processValuationUpdates() {
  if (process.env.SKIP_RABBITMQ === "true") {
    console.log("Skipping RabbitMQ connection.");
    return;
  }

  await initRabbitMQ();
}

module.exports = processValuationUpdates;
