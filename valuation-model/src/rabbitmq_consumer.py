import aio_pika
import json
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValModConsumer:
    def __init__(self):
        self.should_reconnect = False
        self.was_consuming = False

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False

        # TODO: Delete hardcoded env var
        self._url = 'amqp://guest:guest@34.231.140.237'

    async def connect(self):
        logger.info('Connecting to %s', self._url)
        return await aio_pika.connect_robust(self._url)

    async def on_connection_open(self, connection):
        logger.info('Connection opened')
        self._connection = connection
        await self.open_channel()

    async def on_connection_open_error(self, err):
        logger.error('Connection open failed: %s', err)
        await self.reconnect()

    async def on_connection_closed(self, reason):
        self._channel = None
        if self._closing:
            self._connection = None
        else:
            logger.warning('Connection closed, reconnect necessary: %s', reason)
            await self.reconnect()

    async def reconnect(self):
        self.should_reconnect = True
        await self.stop()

    async def open_channel(self):
        logger.info('Creating a new channel')
        self._channel = await self._connection.channel()
        logger.info('Channel opened')
        await self.setup_queue('val_queue')

    async def setup_queue(self, queue_name):
        logger.info('Declaring queue %s', queue_name)
        queue = await self._channel.declare_queue(queue_name, durable=False)
        await self.start_consuming(queue)

    async def start_consuming(self, queue):
        logger.info('Issuing consumer related RPC commands')
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.on_message(message)

    async def on_message(self, message):
        async with message.process():
            logger.info('Received message # %s: %s',
                        message.delivery_tag, message.body)
            await self.process_message(message.body)

    async def process_message(self, body):
        data = json.loads(body)
        processed_data = await self.process_data_with_model(data)
        logger.info('Processed data: %s', processed_data)
        await self.add_to_update_task_queue(processed_data)
        logger.info('Added data to update_task_queue: %s', processed_data)

    async def process_data_with_model(self, data):
        await asyncio.sleep(1)  # Simulating processing time
        return data

    async def add_to_update_task_queue(self, data):
        await self._channel.declare_queue('update_task_queue', durable=False)
        await self._channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(data).encode()),
            routing_key='update_task_queue'
        )

    async def stop_consuming(self):
        if self._channel:
            logger.info('Stopping consuming')
            await self._channel.close()

    async def run_async(self):
        while not self._closing:
            try:
                self._connection = await self.connect()
                await self.on_connection_open(self._connection)
                self._consuming = True
                while self._consuming:
                    await asyncio.sleep(0.1)
            except aio_pika.exceptions.AMQPError as err:
                logger.error("AMQP error: %s", err)
                await asyncio.sleep(5)
            except Exception as err:
                logger.error("Unexpected error: %s", err)
                await asyncio.sleep(5)
            finally:
                await self.stop()

    async def stop(self):
        if not self._closing:
            self._closing = True
            logger.info('Stopping')
            if self._consuming:
                await self.stop_consuming()
            if self._connection:
                await self._connection.close()
            logger.info('Stopped')

async def main():
    consumer = ValModConsumer()
    try:
        await consumer.run_async()
    except KeyboardInterrupt:
        await consumer.stop()

if __name__ == '__main__':
    asyncio.run(main())