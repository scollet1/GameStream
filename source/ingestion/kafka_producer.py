import json
import random
import struct
import umsgpack
from copy import deepcopy
from datetime import datetime
if __name__ != "__main__":
    from kafka import KafkaProducer

def encode_datetime(obj):
    if isinstance(obj, datetime):
        return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}
    return obj

def produce(generator, topic='topic'):
    if __name__ != "__main__":
        bootstrap_servers = ['localhost:9092']
        topic_name = topic
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
    while True:
        event = generator.generate_data()
        if __name__ != "__main__":
            ack = producer.send(
                topic_name,
                json.dumps(event, default=encode_datetime)
            )
            break

if __name__ == "__main__":
    import data_generator
    dg = data_generator.DataGenerator(100)
    produce(dg)
