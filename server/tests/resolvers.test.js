const fs = require("fs");
const path = require("path");
const { ApolloServer } = require("apollo-server-express");
const { gql } = require("apollo-server");
const { createTestClient } = require("apollo-server-testing");
const express = require("express");
const { createServer } = require("http");
const { SubscriptionClient } = require("subscriptions-transport-ws");
const { SubscriptionServer } = require("subscriptions-transport-ws");
const WebSocket = require("ws");
const { ApolloClient, InMemoryCache } = require("@apollo/client/core");
const { WebSocketLink } = require("@apollo/client/link/ws");
const { execute, subscribe } = require("graphql"); // Import execute and subscribe
const { makeExecutableSchema } = require("@graphql-tools/schema");

const typeDefs = gql(
  fs.readFileSync(path.join(__dirname, "../src/schema.gql"), "utf8")
);
const resolvers = require("../src/resolvers");
const pubsub = require("../src/pubsub"); // Use the shared pubsub instance

const schema = makeExecutableSchema({ typeDefs, resolvers });

const app = express();
const httpServer = createServer(app);

const server = new ApolloServer({
  schema,
  context: { pubsub },
});

let subscriptionServer;

beforeAll(async () => {
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

  await new Promise((resolve) => httpServer.listen({ port: 4000 }, resolve));
});

afterAll(async () => {
  await server.stop();
  subscriptionServer.close();
  await new Promise((resolve) => httpServer.close(resolve));
});

const CREATE_TASK = gql`
  mutation CreateTask($input: CreateTaskInput!) {
    createTask(input: $input) {
      id
      desc
      folderPath
      walletAddress
      status
      valuation
    }
  }
`;

const TASK_CREATED = gql`
  subscription TaskCreated($folderPath: String!) {
    taskCreated(folderPath: $folderPath) {
      id
      desc
      folderPath
      walletAddress
      status
      valuation
    }
  }
`;

const testTaskInput = {
  id: "1",
  desc: "Test Task",
  folderPath: "/test/path",
  walletAddress: "0x123",
};

test("creates a task and returns the created task object", async () => {
  const { mutate } = createTestClient(server);

  const res = await mutate({
    mutation: CREATE_TASK,
    variables: { input: testTaskInput },
  });

  console.log("Create Task Mutation Response:", res.data);
  expect(res.data.createTask).toEqual({
    id: "1",
    desc: "Test Task",
    folderPath: "/test/path",
    walletAddress: "0x123",
    status: "Pending",
    valuation: 0,
  });
});

test("publishes task creation events to the correct subscription channel", (done) => {
  const wsClient = new SubscriptionClient(
    `ws://localhost:4000/graphql`,
    { reconnect: true },
    WebSocket
  );

  wsClient.onConnected(() => {
    const link = new WebSocketLink(wsClient);

    const client = new ApolloClient({
      link,
      cache: new InMemoryCache(),
    });

    const observable = client.subscribe({
      query: TASK_CREATED,
      variables: { folderPath: "/test/path" },
    });

    observable.subscribe({
      next(response) {
        console.log("Subscription Response:", response.data);
        try {
          expect(response.data.taskCreated).toEqual({
            __typename: "Task",
            id: "1",
            desc: "Test Task",
            folderPath: "/test/path",
            walletAddress: "0x123",
            status: "Pending",
            valuation: 0,
          });
          done();
        } catch (error) {
          done(error);
        } finally {
          wsClient.close();
        }
      },
      error(err) {
        done(err);
        wsClient.close();
      },
    });

    setTimeout(() => {
      const { mutate } = createTestClient(server);
      mutate({
        mutation: CREATE_TASK,
        variables: { input: testTaskInput },
      }).catch(done);
    }, 1000);
  });

  wsClient.onError((error) => {
    done(error);
  });
}, 20000); // Increase the timeout to 20000 ms
