'''
Commission sql queries
'''
from django.db import connection
import decimal

class SqlHelper(object):
    ''' Advanced Filter '''

    _ALREADY_EXISTS_STORE = r'''SELECT * FROM store_store WHERE retailer_business_id=%s and ( 6373 * acos( cos( radians( %s ) ) * cos(radians( latitude ) ) * cos( radians( longitude ) - radians( %s ) ) + sin(radians( %s ) ) * sin( radians( latitude ) ) ) ) <= 500'''
        
    @staticmethod
    def get_already_business(retailer_business, latitude, longitude):
        '''Execute User Commission Sql'''
        with connection.cursor() as cursor:
            cursor.execute(
                SqlHelper._ALREADY_EXISTS_STORE, [int(retailer_business), latitude, longitude, latitude])
            data = cursor.fetchall()
            return data
