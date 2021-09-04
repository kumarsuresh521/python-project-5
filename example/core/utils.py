import json
from urllib.parse import urlencode

import requests

from django.conf import settings
from kafka import KafkaProducer


def intializekafka(topic, request):
    if settings.ENABLE_KAFKA:
        producer = KafkaProducer(bootstrap_servers=settings.HUB_EXAMPLE_USER_KAFKA_SERVER, value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        producer.send(topic, request)
        producer.flush()
    return True

class VerifyBankAccount(object):
    
    @staticmethod
    def validate_account(params):
        '''
        [{'Cause': 'The SortCode parameter was not valid.', 'Error': '1002',
         'Resolution': 'The SortCode parameter should be 6 digits in the form 00-00-00 or 000000. It should be prefixed with leading 0s if necessary.', 
         'Description': 'SortCode Invalid'}]
        '''
        response_data = {}
        bank_url = settings.BANK_ACCOUNT_VERIFY_URL
        params['Key'] = settings.BANK_ACCOUNT_VERIFY_KEY
        
        try:
            response = requests.get(url=bank_url , params=params)
            data = response.json()
            
            if 'IsCorrect' in data[0].keys():
                if data[0]['IsCorrect'] == 'False':
                    response_data['message'] = data[0]['StatusInformation']
                    response_data['verify'] = False
                else:
                    response_data['message'] = data[0]['StatusInformation']
                    response_data['verify'] = True
            elif 'Error' in data[0].keys():
                response_data['message'] = data[0]['Resolution']
                response_data['verify'] = False
        except:
            response_data['message'] = 'Bank Account URL not accessible'
            response_data['verify'] = False
        
        return response_data
