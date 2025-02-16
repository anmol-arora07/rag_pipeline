from confluent_kafka import Producer
import json

conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker address
    'client.id': 'fastapi-client'
}

producer = Producer(conf)

# Function to send messages to Kafka
def send_to_kafka(topic, file_id, message):
    producer.produce(topic, key=file_id, value=json.dumps(message))
    producer.flush()  # Ensure the message is sent