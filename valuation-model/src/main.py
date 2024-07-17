import pika
import json
import os
import time
import logging
from pika.adapters.select_connection import SelectConnection

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
        self._url = 'amqp://guest:guest@44.209.101.218'

    def connect(self):
        logger.info('Connecting to %s', self._url)
        return pika.SelectConnection(
            parameters=pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed)

    def on_connection_open(self, _unused_connection):
        logger.info('Connection opened')
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        logger.error('Connection open failed: %s', err)
        self.reconnect()

    def on_connection_closed(self, _unused_connection, reason):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logger.warning('Connection closed, reconnect necessary: %s', reason)
            self.reconnect()

    def reconnect(self):
        self.should_reconnect = True
        self.stop()

    def open_channel(self):
        logger.info('Creating a new channel')
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        logger.info('Channel opened')
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_queue('val_queue')

    def add_on_channel_close_callback(self):
        logger.info('Adding channel close callback')
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        logger.warning('Channel %i was closed: %s', channel, reason)
        self._channel = None
        if not self._closing:
            self._connection.close()

    def setup_queue(self, queue_name):
        logger.info('Declaring queue %s', queue_name)
        self._channel.queue_declare(queue=queue_name, durable=False, callback=self.on_queue_declareok)

    def on_queue_declareok(self, _unused_frame):
        logger.info('Queue declared')
        self.start_consuming()

    def start_consuming(self):
        logger.info('Issuing consumer related RPC commands')
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self._consumer_tag = self._channel.basic_consume('val_queue', self.on_message)
        self.was_consuming = True
        self._consuming = True

    def on_consumer_cancelled(self, method_frame):
        logger.info('Consumer was cancelled remotely, shutting down: %r', method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        logger.info('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        self.process_message(body)
        self.acknowledge_message(basic_deliver.delivery_tag)

    def process_message(self, body):
        data = json.loads(body)
        processed_data = self.process_data_with_model(data)
        logger.info('Processed data: %s', processed_data)
        self.add_to_task_queue(processed_data)
        logger.info('Added data to server_queue: %s', processed_data)

    def process_data_with_model(self, data):
        time.sleep(1)
        return data

    def add_to_task_queue(self, data):
        self._channel.queue_declare(queue='server_queue', durable=False)
        self._channel.basic_publish(exchange='',
                                    routing_key='server_queue',
                                    body=json.dumps(data))

    def acknowledge_message(self, delivery_tag):
        logger.info('Acknowledging message %s', delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def stop_consuming(self):
        if self._channel:
            logger.info('Sending a Basic.Cancel RPC command to RabbitMQ')
            cb = lambda _: self._connection.ioloop.stop()
            self._channel.basic_cancel(self._consumer_tag, cb)

    def run(self):
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        if not self._closing:
            self._closing = True
            logger.info('Stopping')
            if self._consuming:
                self.stop_consuming()
                self._connection.ioloop.start()
            else:
                self._connection.ioloop.stop()
            logger.info('Stopped')

def main():
    consumer = ValModConsumer()
    try:
        consumer.run()
    except KeyboardInterrupt:
        consumer.stop()

if __name__ == '__main__':
    main()