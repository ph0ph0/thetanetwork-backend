const { ApolloServer } = require("apollo-server-express");
const express = require("express");
const { createServer } = require("http");
const { useServer } = require("graphql-ws/lib/use/ws");
const { WebSocketServer } = require("ws");
const { makeExecutableSchema } = require("@graphql-tools/schema");
const gql = require("graphql-tag");
const cors = require("cors");

const typeDefs = gql`
  ${require("fs").readFileSync(
    require("path").join(__dirname, "schema.gql"),
    "utf8"
  )}
`;
const resolvers = require("./resolvers");
const pubsub = require("./pubsub");
const processValuationUpdates = require("./processValuationUpdates");

const schema = makeExecutableSchema({ typeDefs, resolvers });

const app = express();
app.use(cors());
const httpServer = createServer(app);

const wsServer = new WebSocketServer({
  server: httpServer,
  path: "/graphql",
});

const serverCleanup = useServer(
  {
    schema,
    context: (ctx, msg, args) => {
      return { pubsub };
    },
    onConnect: (ctx) => {
      console.log("Connected to websocket");
    },
    onDisconnect: (ctx) => {
      console.log("Disconnected from websocket");
    },
    onError: (ctx, message, errors) => {
      console.error("Subscription error:", message, errors);
    },
  },
  wsServer
);

const server = new ApolloServer({
  schema,
  context: ({ req, res }) => ({ req, res, pubsub }),
  plugins: [
    {
      async serverWillStart() {
        return {
          async drainServer() {
            await serverCleanup.dispose();
          },
        };
      },
    },
  ],
});

(async () => {
  await server.start();
  server.applyMiddleware({ app });

  httpServer.listen({ port: 4000, host: "0.0.0.0" }, () => {
    console.log("Started latest server fresh");
    console.log(`Server ready at http://0.0.0.0:4000${server.graphqlPath}`);
    console.log(
      `Subscriptions ready at ws://0.0.0.0:4000${server.graphqlPath}`
    );
  });

  processValuationUpdates();
})();
