import pika
import sys

def test_rabbitmq_connection(rabbitmq_url):
    try:
        print(f"Attempting to connect to RabbitMQ at {rabbitmq_url}...")
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
        channel = connection.channel()

        # Declare a queue
        channel.queue_declare(queue='test_queue', durable=False)

        # Publish a message
        message = 'Hello, RabbitMQ!'
        channel.basic_publish(exchange='',
                              routing_key='test_queue',
                              body=message)
        print(f" [x] Sent '{message}'")

        # Close the connection
        connection.close()
        print("Connection to RabbitMQ successful and message sent.")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}")
    except pika.exceptions.ChannelError as e:
        print(f"Channel error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_rabbitmq_connection.py <rabbitmq_url>")
        sys.exit(1)

    rabbitmq_url = sys.argv[1]
    test_rabbitmq_connection(rabbitmq_url)
