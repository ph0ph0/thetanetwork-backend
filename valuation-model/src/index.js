const express = require("express");
const { graphqlHTTP } = require("express-graphql");
const { buildSchema } = require("graphql");
const ValModConsumer = require("./rabbitmqConsumer");

// GraphQL schema
const schema = buildSchema(`
  type Query {
    status: String
  }
`);

// Root resolver
const root = {
  status: () => "Running",
};

async function startServices() {
  // Start the RabbitMQ consumer
  const consumer = new ValModConsumer();
  const consumerPromise = consumer.runAsync();

  // Start the GraphQL server
  const app = express();
  app.use(
    "/graphql",
    graphqlHTTP({
      schema: schema,
      rootValue: root,
      graphiql: false,
    })
  );

  app.get("/graphiql", (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>GraphiQL</title>
            <link href="https://unpkg.com/graphiql/graphiql.min.css" rel="stylesheet" />
        </head>
        <body style="margin: 0;">
            <div id="graphiql" style="height: 100vh;"></div>
            <script crossorigin src="https://unpkg.com/react/umd/react.production.min.js"></script>
            <script crossorigin src="https://unpkg.com/react-dom/umd/react-dom.production.min.js"></script>
            <script crossorigin src="https://unpkg.com/graphiql/graphiql.min.js"></script>
            <script>
                const fetcher = GraphiQL.createFetcher({ url: '/graphql' });
                ReactDOM.render(
                    React.createElement(GraphiQL, { fetcher: fetcher }),
                    document.getElementById('graphiql'),
                );
            </script>
        </body>
        </html>
        `);
  });

  const server = app.listen(8080, "0.0.0.0", () => {
    console.log("GraphQL server started at http://0.0.0.0:8080/graphql");
    console.log("GraphiQL interface available at http://0.0.0.0:8080/graphiql");
    console.log("RabbitMQ consumer started");
  });

  // Keep the services running
  try {
    await Promise.all([
      consumerPromise,
      new Promise((resolve) => server.on("close", resolve)),
    ]);
  } finally {
    server.close();
    await consumer.stop();
  }
}

startServices().catch(console.error);
