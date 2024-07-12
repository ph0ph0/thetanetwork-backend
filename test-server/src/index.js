const { ApolloServer } = require("apollo-server-express");
const express = require("express");
const { createServer } = require("http");
const { makeExecutableSchema } = require("@graphql-tools/schema");
const gql = require("graphql-tag");

const typeDefs = gql`
  ${require("fs").readFileSync(
    require("path").join(__dirname, "schema.gql"),
    "utf8"
  )}
`;

const resolvers = {
  Query: {
    test: () => true,
  },
};

const schema = makeExecutableSchema({ typeDefs, resolvers });

const app = express();
const httpServer = createServer(app);

const server = new ApolloServer({
  schema,
  context: ({ req, res }) => ({ req, res }),
});

(async () => {
  await server.start();
  server.applyMiddleware({ app });

  httpServer.listen({ port: 4000 }, () => {
    console.log(`Server ready at http://localhost:4000${server.graphqlPath}`);
  });
})();
