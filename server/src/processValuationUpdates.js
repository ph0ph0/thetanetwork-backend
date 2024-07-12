const amqp = require("amqplib");
const pubsub = require("./pubsub");

async function processValuationUpdates() {
  let rabbitmqUrl;
  if (process.env.SKIP_RABBITMQ === "true") {
    console.log("Skipping RabbitMQ connection.");
    return;
  } else {
    rabbitmqUrl = process.env.RABBITMQ_URL || "amqp://rabbitmq";
  }

  const connection = await amqp.connect(rabbitmqUrl);
  const channel = await connection.createChannel();
  await channel.assertQueue("update_task_queue", { durable: false });

  channel.consume("update_task_queue", (msg) => {
    if (msg !== null) {
      console.log("Received message from queue");
      const { valuation, walletAddress, folderPath, id, desc, status } =
        JSON.parse(msg.content.toString());

      let task = { valuation, walletAddress, folderPath, id, desc, status };
      task.valuation = valuation;
      task.status = "Completed";

      console.log(`Task updated: ${JSON.stringify(task)}`);
      pubsub.publish(`TASK_UPDATED_${folderPath}`, { taskUpdated: task });

      channel.ack(msg);
    }
  });
}

module.exports = processValuationUpdates;
