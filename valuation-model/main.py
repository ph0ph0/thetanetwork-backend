import pika
import json
import os

def callback(ch, method, properties, body):
    data = json.loads(body)
    process_data_with_model(data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def process_data_with_model(data):
    # This function will call your actual model processing
    pass

def main():
    rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://localhost')
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue='queue_name', durable=False)

    channel.basic_consume(queue='queue_name', on_message_callback=callback)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    main()
