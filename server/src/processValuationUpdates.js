const amqp = require("amqplib");
const pubsub = require("./pubsub");

async function processValuationUpdates() {
  if (process.env.SKIP_RABBITMQ === "true") {
    console.log("Skipping RabbitMQ connection.");
    return;
  }

  const connection = await amqp.connect("amqp://localhost");
  const channel = await connection.createChannel();
  await channel.assertQueue("update_task_queue", { durable: false });

  channel.consume("update_task_queue", (msg) => {
    if (msg !== null) {
      const { valuation, taskId, walletAddress, folderPath } = JSON.parse(
        msg.content.toString()
      );

      let task = {};
      task.valuation = valuation;
      task.status = "Completed";

      pubsub.publish(`TASK_UPDATED_${folderPath}`, { taskUpdated: task });

      channel.ack(msg);
    }
  });
}

module.exports = processValuationUpdates;
