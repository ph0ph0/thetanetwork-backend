import pika
import json
import os
import time

def callback(ch, method, properties, body):
    data = json.loads(body)
    processed_data = process_data_with_model(data)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f'Processed data: {processed_data}')
    
    # Add processed data to val_queue
    add_to_task_queue(processed_data)
    print(f'Added data to val_queue: {processed_data}')

def process_data_with_model(data):
    # Simulate processing the data
    time.sleep(1)
    # Here you would include the actual SoM model processing logic
    # For now, let's assume processed data is the same as input data
    return data

def add_to_task_queue(data):
    rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://localhost')
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue='update_task_queue', durable=False)
    
    channel.basic_publish(exchange='',
                          routing_key='update_task_queue',
                          body=json.dumps(data))
    connection.close()

def main():
    rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://localhost')
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue='val_queue', durable=False)

    channel.basic_consume(queue='val_queue', on_message_callback=callback)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()
