from confluent_kafka import Consumer, KafkaException, KafkaError
import json
from rag.database.store_embeddings import store_embeddings

# Kafka consumer configuration
conf = {
    'bootstrap.servers': 'localhost:9092',  # Kafka broker address
    'group.id': 'file-processing-group',    # Consumer group ID
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

# Subscribe to the 'file-upload-topic'
consumer.subscribe(['file-upload-topic'])

def process_file(file_data):
    # Example of processing file data (you can use it for sending to a vector database)
    print(f"Processing file {file_data['filename']} with ID {file_data['documentId']}")
    # Here you can add the logic for sending the data to the vector database
    store_embeddings(file_path=file_data['filePath'], document_id=file_data['documentId'])
    print(f"Done for file {file_data['filename']} with ID {file_data['documentId']}")

def consume_messages():
    while True:
        msg = consumer.poll(timeout=1.0)  # Poll Kafka for messages

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())
        else:
            file_data = json.loads(msg.value().decode('utf-8'))
            process_file(file_data)

