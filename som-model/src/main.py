import logging
import pika
import json
import os
import time

logging.basicConfig(level=logging.INFO)

def callback(ch, method, properties, body):
    logging.info(f'Received data: {body}')
    data = json.loads(body)
    processed_data = process_data_with_model(data)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    logging.info(f'Processed data: {processed_data}')
    
    # Add processed data to server_queue
    add_to_server_queue(processed_data)
    logging.info(f'Added data to server_queue: {processed_data}')

def process_data_with_model(data):
    # Simulate val mod processing the data
    time.sleep(1)
    return data

def add_to_server_queue(data):
    rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://localhost')
    # TODO: Delete hardcoded env var
    rabbitmq_url = 'amqp://guest:guest@44.209.101.218'
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue='server_queue', durable=False)
    
    channel.basic_publish(exchange='',
                          routing_key='server_queue',
                          body=json.dumps(data))
    connection.close()

def main():
    logging.info('Starting som model service')
    rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://localhost')
    logging.info(f'Connecting to RabbitMQ at {rabbitmq_url}')
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue='val_queue', durable=False)
    logging.info('val model connected to RabbitMQ')

    channel.basic_consume(queue='val_queue', on_message_callback=callback)
    logging.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()
