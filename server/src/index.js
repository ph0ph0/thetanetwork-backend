const { ApolloServer } = require("apollo-server-express");
const express = require("express");
const { createServer } = require("http");
const { execute, subscribe } = require("graphql");
const { SubscriptionServer } = require("subscriptions-transport-ws");
const { makeExecutableSchema } = require("@graphql-tools/schema");
const typeDefs = require("./schema");
const resolvers = require("./resolvers");
const pubsub = require("./pubsub"); // Use the shared pubsub instance

const schema = makeExecutableSchema({ typeDefs, resolvers });

const app = express();
const httpServer = createServer(app);

const server = new ApolloServer({
  schema,
  context: ({ req, res }) => ({ req, res, pubsub }),
  plugins: [
    {
      async serverWillStart() {
        return {
          async drainServer() {
            subscriptionServer.close();
          },
        };
      },
    },
  ],
});

let subscriptionServer;

(async () => {
  await server.start();
  server.applyMiddleware({ app });

  subscriptionServer = SubscriptionServer.create(
    {
      schema,
      execute,
      subscribe,
      onConnect: () => {
        console.log("Connected to websocket");
      },
    },
    {
      server: httpServer,
      path: server.graphqlPath,
    }
  );

  httpServer.listen({ port: 4000 }, () => {
    console.log(`Server ready at http://localhost:4000${server.graphqlPath}`);
    console.log(
      `Subscriptions ready at ws://localhost:4000${server.graphqlPath}`
    );
  });
})();
