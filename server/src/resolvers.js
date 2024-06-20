const pubsub = require("./pubsub"); // Use the shared pubsub instance

const resolvers = {
  Subscription: {
    taskUpdated: {
      subscribe: (_, { folderPath }) => {
        return pubsub.asyncIterator(`TASK_CREATED_${folderPath}`);
      },
    },
  },
  Mutation: {
    createTask: (_, { input }) => {
      const task = { ...input, status: "Pending", valuation: 0 };
      pubsub.publish(`TASK_CREATED_${task.folderPath}`, { taskUpdated: task });
      return task;
    },
  },
};

module.exports = resolvers;
