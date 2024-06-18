const pubsub = require("./pubsub"); // Use the shared pubsub instance

const resolvers = {
  Subscription: {
    taskCreated: {
      subscribe: (_, { folderPath }) => {
        return pubsub.asyncIterator(`TASK_CREATED_${folderPath}`);
      },
    },
  },
  Mutation: {
    createTask: (_, { input }) => {
      const task = { ...input, status: "Pending", valuation: 0 };
      pubsub.publish(`TASK_CREATED_${task.folderPath}`, { taskCreated: task });
      return task;
    },
  },
};

module.exports = resolvers;
