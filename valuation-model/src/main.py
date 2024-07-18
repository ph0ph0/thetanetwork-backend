import asyncio
from aiohttp import web
import graphene
from graphql import graphql
from rabbitmq_consumer import ValModConsumer

class Query(graphene.ObjectType):
    status = graphene.String()

    def resolve_status(self, info):
        return "Running"

schema = graphene.Schema(query=Query)

async def graphql_handler(request):
    data = await request.json()
    result = await graphql(
        schema.graphql_schema,
        data.get('query'),
        variable_values=data.get('variables'),
        operation_name=data.get('operationName'),
    )
    response_data = {
        'data': result.data,
        'errors': [str(error) for error in result.errors] if result.errors else None
    }
    return web.json_response(response_data)

async def graphiql_handler(request):
    html = '''
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
    '''
    return web.Response(text=html, content_type='text/html')

async def start_services():
    # Start the RabbitMQ consumer
    consumer = ValModConsumer()
    consumer_task = asyncio.create_task(consumer.run_async())

    # Start the GraphQL server
    app = web.Application()
    app.router.add_post('/graphql', graphql_handler)
    app.router.add_get('/graphiql', graphiql_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()

    print("GraphQL server started at http://0.0.0.0:8080/graphql")
    print("GraphiQL interface available at http://0.0.0.0:8080/graphiql")
    print("RabbitMQ consumer started")

    # Keep the services running
    try:
        await asyncio.gather(consumer_task, asyncio.Future())
    finally:
        await runner.cleanup()
        consumer.stop()

if __name__ == '__main__':
    asyncio.run(start_services())