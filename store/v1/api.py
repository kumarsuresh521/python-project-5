'''
Api requests for store module
'''
from example.core.helper import CustomPagination
from rest_framework import generics
from store.models import Store
from store.serializers_api import StoreSerializers, StoreDetailSerializers
import json

class ListStoreView(generics.ListAPIView):
    '''
    Store list api 
    '''
    serializer_class = StoreSerializers
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Store.objects.filter(retailer_business__retailer_id=self.kwargs['user_id'], is_active=True).order_by('-id')
        if 'store_ids' in self.request.query_params:
            ids = self.request.query_params['store_ids']
            ids = [int(x) for x in ids.split(",")]
            queryset = queryset.filter(id__in=ids)
        return queryset

class StoreView(generics.RetrieveAPIView):
    '''
    Store detail api
    '''
    serializer_class = StoreDetailSerializers

    def get_object(self):
        store_obj = Store.objects.filter(id=self.kwargs['store_id'], is_active=True).first()
        return store_obj

class EvidenceStoreListingView(generics.ListAPIView):
    '''
    Store list api 
    '''
    serializer_class = StoreSerializers
    
    def get_queryset(self):
        queryset = Store.objects.filter(is_active=True)
        if 'store_ids' in self.request.query_params:
            ids = self.request.query_params['store_ids']
            ids = [int(x) for x in ids.split(",")]
            queryset = queryset.filter(id__in=ids)
        
        return queryset

class StaffDetailStoresListingView(generics.ListAPIView):
    '''
    Store list api 
    '''
    serializer_class = StoreSerializers
    
    def get_queryset(self):
        queryset = Store.objects.filter(is_active=True, id__in=json.loads(self.request.query_params['store_ids']))
        return queryset