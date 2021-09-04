import json
import os

import django

from kafka import KafkaConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "example.settings")
django.setup()

from django.conf import settings

'''
Consumer for update retailer in microservices.
'''
consumer = KafkaConsumer('update_retailer', bootstrap_servers=settings.HUB_EXAMPLE_USER_KAFKA_SERVER)
for msg in consumer:
    request_data = json.loads(msg.value)
consumer.flush()
