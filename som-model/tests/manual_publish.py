import pika

def manual_publish():
    rabbitmq_url = 'amqp://localhost'
    connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
    channel = connection.channel()
    channel.queue_declare(queue='som_queue', durable=False)
    channel.basic_publish(exchange='', routing_key='som_queue', body='{"test": "message"}')
    connection.close()

manual_publish()
