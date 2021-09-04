'''
Api requests for store module
'''
import json
from collections import OrderedDict

import django_filters
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection, transaction
from django.db.models import Case, Count, IntegerField, Q, Sum, Value, When
from django.http import Http404
from django.utils.crypto import get_random_string
from django_filters import rest_framework as rest_filters
from example.core.constants import ADMIN_PAGE_SIZE
from example.core.db.sql import SqlHelper
from example.core.helper import CustomPagination
from example.core.utils import intializekafka
from rest_framework import filters, generics
from rest_framework.response import Response
from store.filters import RetailerStoreFilter, StoreFilter
from store.models import *
from store.serializers_web import *

from ..message import *


def filter_store(queryset, filter_params):
    
    if filter_params.get('fascia', ''):
        queryset = queryset.filter(fascia__id=filter_params.get('fascia', ''))
    if filter_params.get('wholesaler', ''):
        queryset = queryset.filter(wholesaler__id=filter_params.get('wholesaler', ''))
    if filter_params.get('county', ''):
        queryset = queryset.filter(county__id=filter_params.get('county', ''))
    if filter_params.get('licensed', ''):
        queryset = queryset.filter(licensing_status=filter_params.get('licensed', ''))
    if filter_params.get('forecourt', ''):
        queryset = queryset.filter(forecourt=filter_params.get('forecourt', ''))
    if filter_params.get('epos', ''):
        queryset = queryset.filter(epos__id=filter_params.get('epos', ''))
    if filter_params.get('from_turnover', '') and filter_params.get('to_turnover', ''):
        queryset = queryset.filter(average_weekly_turnover__range=(filter_params.get('from_turnover', ''),
                                                        filter_params.get('to_turnover', '')))
    if filter_params.get('from_footfall', '') and filter_params.get('to_footfall', ''):
        queryset = queryset.filter(average_weekly_footfall__range=(filter_params.get('from_footfall', ''),
                                                        filter_params.get('to_footfall', '')))
    if filter_params.get('from_size', '') and filter_params.get('to_size', ''):
        queryset = queryset.filter(store_size__range=(filter_params.get('from_size', ''),
                                                        filter_params.get('to_size', '')))
    if filter_params.get('from_avg_basket', '') and filter_params.get('to_avg_basket', ''):
        queryset = queryset.filter(average_basket_spend__range=(filter_params.get('from_avg_basket', ''),
                                                        filter_params.get('to_avg_basket', '')))
    return queryset


class ListStoreByIdView(generics.ListAPIView):
    '''
    Store list api 
    '''
    serializer_class = StoreSerializers
    pagination_class = CustomPagination
    
    def get_queryset(self):
        queryset = Store.objects.all().order_by('-id')
        if 'store_ids' in self.request.query_params:
            ids = self.request.query_params['store_ids']
            ids = [int(x) for x in ids.split(",")]
            queryset = queryset.filter(id__in=ids)
        return queryset
    

class ListStoreView(generics.CreateAPIView):
    '''
    Store list api 
    '''
    serializer_class = AllStoreSerializers
    pagination_class = CustomPagination
    filter_backends = filters.OrderingFilter
    ordering_fields = ('id', 'name')
    
    def get_queryset(self):
        query_params = Q(retailer_business__retailer_id__in=self.request.data.get('retailer_ids'))
        if self.request.data.get('store_status'):
            query_params = query_params & Q(store_status=self.request.data.get('store_status'))
        return Store.objects.filter(query_params).order_by('-id')

    def post(self, request, *args, **kwargs):
        _ = self
        requested_data = self.request.data
        filter_obj = RetailerStoreFilter(requested_data, queryset=self.get_queryset())

        page_number = requested_data.get('page', 1)

        result_list = Paginator(filter_obj.qs, ADMIN_PAGE_SIZE)

        try:
            page_obj = result_list.page(page_number)
        except PageNotAnInteger:
            page_obj = result_list.page(1)
        except EmptyPage:
            page_obj = result_list.page(result_list.num_pages)

        next_page = int(page_obj.number) + 1 if page_obj.has_next() else None
        previous_page = int(page_obj.number) - 1 if page_obj.has_previous() else None

        response = AllStoreSerializers(page_obj.object_list, many=True).data
        return Response(OrderedDict([
            ('next', next_page),
            ('previous', previous_page),
            ('total_count', page_obj.paginator.count),
            ('results', response)
        ]))


class RetailerAllStoreView(generics.ListAPIView):
    '''
    Store list api 
    '''
    serializer_class = AllStoreSerializers
    pagination_class = CustomPagination
    
    def get_queryset(self):
        params = Q(retailer_business__retailer_id=self.kwargs['retailer_id'])
        if self.request.GET.get('store_ids', ''):
            params = params & Q(id__in=json.loads(self.request.GET.get('store_ids', '')))
        return Store.objects.filter(params).order_by('-id')


class CreateStoreView(generics.CreateAPIView):
    '''
    Store create api 
    '''
    serializer_class = StoreSerializers

    def post(self, request, *args, **kwargs):
        _ = self
        response_data = {}
        retailer_business = self.request.data.get('retailer_business')
        latitude = self.request.data.get('latitude', None)
        longitude = self.request.data.get('longitude', None)
        if latitude and longitude:
            business = SqlHelper.get_already_business(retailer_business, latitude, longitude)
            request.data['another_store_available'] = len(business) > 0
        
        serializer = StoreSerializers(data=request.data)
        with transaction.atomic():
            if serializer.is_valid():
                store = serializer.save()
                if settings.ENABLE_KAFKA:
                    intializekafka('create_store', serializer.data)
                response_data[SUCCESS] = CREATED_SUCCESSFULL
                status_code = HTTP_200_SUCCESS
            else:
                response_data[MESSAGE] = serializer.errors
                status_code = HTTP_API_ERROR
            return Response(response_data, status=status_code)
        return store

class UpdateStoreView(generics.UpdateAPIView):
    '''
    Store Update api 
    '''
    serializer_class = StoreSerializers
    def get_object(self):
        return Store.objects.get(id=self.kwargs['id'])

class DeleteStoreView(generics.DestroyAPIView):
    '''
    Store Delete api 
    '''
    serializer_class = StoreSerializers
    def get_object(self):
        return Store.objects.get(id=self.kwargs['id'])


class ListFasciaView(generics.ListAPIView):
    '''
    Fascia list api 
    '''
    serializer_class = FasciaSerializers
    queryset = Fascia.objects.filter(is_active=True).order_by('name')
    

class ListWholesalerView(generics.ListAPIView):
    '''
    Wholesaler list api 
    '''
    serializer_class = WholesalerSerializers
    queryset = Wholesaler.objects.filter(is_active=True).order_by('name')
    

class ListEposSystemView(generics.ListAPIView):
    '''
    EposSystem list api 
    '''
    serializer_class = EposSystemSerializers
    queryset = EposSystem.objects.filter(is_active=True).order_by('name')
    

class ListCountyView(generics.ListAPIView):
    '''
    EposSystem list api 
    '''
    serializer_class = CountySerializers

    def get_queryset(self):
        query_params = Q(is_active=True)

        if self.request.GET.get('country_id', None):
            query_params = query_params & Q(country_id=self.request.GET.get('country_id'))
        return County.objects.filter(query_params).order_by('name')


class ListCountryView(generics.ListAPIView):
    '''
    EposSystem list api 
    '''
    serializer_class = CountrySerializers
    pagination_class = CustomPagination
    queryset = Country.objects.filter(is_active=True).order_by('name')

 
class ListRetailersView(generics.ListAPIView):
    '''
    Retailers View
    '''
    serializer_class = RetailerStoreSerializer
    filter_class = StoreFilter
    filter_backends = (rest_filters.DjangoFilterBackend,)
    pagination_class = CustomPagination

    def get_queryset(self):
        _ = self.__class__.__name__
        return Store.objects.filter(retailer_business__is_active=True, is_active=True,
                                    store_status=Store.APPROVED).order_by('retailer_business', '-id').distinct('retailer_business')


class ListRetailersBusinessView(generics.ListCreateAPIView):
    '''
    Retailers View
    '''
    filter_class = RetailerStoreFilter
    filter_backends = (rest_filters.DjangoFilterBackend,)

    def get_queryset(self):
        request_obj = self.request.data
        retailer_ids = request_obj.get('retailer_ids', '')
        query_vars = Q()
        if retailer_ids:
            query_vars = query_vars & Q(retailer_business__retailer_id__in=retailer_ids)
        store_ids = Store.objects.filter(query_vars).values_list('id').distinct('retailer_business__retailer_id')
        return Store.objects.filter(id__in=store_ids)


    def post(self, request, *args, **kwargs):
        _ = self
        requested_data = self.request.data
        filter_obj = RetailerStoreFilter(requested_data, queryset=self.get_queryset())
        data = RetailerBusinessStoreSerializer(filter_obj.qs, many=True).data
        response = []
        for store in data:
            if store['total_stores'] >= requested_data['store_count_from'] and store['total_stores'] <= requested_data['store_count_to']:
                response.append(store)
        return Response(response)




class ListBusinessStoresView(generics.ListAPIView):
    '''
    Retailers View
    '''
    serializer_class = BusinessStoreSerializer
    pagination_class = CustomPagination
    queryset = Store.objects.filter(is_active=True).distinct()
    
    def get_serializer_context(self):
        context = super(ListBusinessStoresView, self).get_serializer_context()
        queryset = self.queryset.filter(retailer_business=self.kwargs['id']).distinct()
        query_params = self.request.query_params
        matched_stores = filter_store(queryset, query_params).values_list('id', flat=True)
        context.update({'matched_stores': matched_stores, 'search_text':self.request.query_params.get('search', None)})
        return context

    def get_queryset(self):
        queryset = self.queryset.filter(retailer_business=self.kwargs['id'])
        search_text = self.request.query_params.get('search')
        
        if search_text:
            search_term_q = Q(Q(postcode__icontains=search_text) | Q(name__icontains=search_text) |
                Q(address1__icontains=search_text) | Q(address2__icontains=search_text)
                | Q(town__icontains=search_text) | Q(fascia__name__icontains=search_text) | Q(county__name__icontains=search_text) |
                Q(wholesaler__name__icontains=search_text) | Q(retailer_business__name__icontains=search_text))
            search_queryset = queryset.filter(search_term_q).order_by('name')
            other_queryset = queryset.exclude(id__in=search_queryset).order_by('name')
            queryset = search_queryset.union(other_queryset)
        return queryset


class FilterBusinessStoresView(generics.ListAPIView):
    '''
    Retailers View
    '''
    serializer_class = FilterBusinessStoreSerializer
    filter_class = StoreFilter

    def get_queryset(self):
        return Store.objects.filter(retailer_business=self.kwargs['id']).distinct()


class SearchStore(generics.ListAPIView):
    '''
    API view for searching stores
    '''
    serializer_class = SearchStoreSerializer
    pagination_class = CustomPagination
    queryset = Store.objects.filter(is_active=True)
    def get_queryset(self):
        search_query = self.request.query_params.get('query', '')
        retailer_ids = self.request.query_params.get('retailer_ids', '')
        ids = ''
        if retailer_ids:
            ids = [int(x) for x in retailer_ids.split(",")]

        queryset = self.queryset
        if search_query != '':
            search_term_q = Q()
            for search_text in search_query.split(','):
                search_term_q = search_term_q | Q(Q(retailer_business__retailer_id__in=ids) | Q(postcode__icontains=search_text) | Q(name__icontains=search_text) |
                    Q(address1__icontains=search_text) | Q(address2__icontains=search_text)
                    | Q(town__icontains=search_text) | Q(fascia__name__icontains=search_text) | Q(county__name__icontains=search_text) |
                    Q(wholesaler__name__icontains=search_text) | Q(retailer_business__name__icontains=search_text))
            queryset = queryset.filter(search_term_q)

        return queryset.order_by('retailer_business', 'name').distinct('retailer_business')


class RetailerBusinessList(generics.ListAPIView):
    serializer_class = RetailerBusinessSerializer

    def get_queryset(self):
        business_ids = self.request.query_params['business_ids']
        business_ids = [int(x) for x in business_ids.split(",")]
        queryset = RetailerBusiness.objects.filter(id__in=business_ids).order_by('-id')
        return queryset

class RetailerBusinessView(generics.CreateAPIView):
    '''
    Business create api 
    '''
    serializer_class = RetailerBusinessCreateSerializer
    
    def post(self, request, *args, **kwargs):
        _ = self
        response_data = {}
        request.data['unique_string'] = get_random_string(length=32)
        bank_data = request.data.pop('bank_details')
        serializer = RetailerBusinessCreateSerializer(data=request.data)
        with transaction.atomic():
            if serializer.is_valid():
                sid = transaction.savepoint()
                business = serializer.save()
                if settings.ENABLE_KAFKA:
                    intializekafka('create_business', serializer.data)
                bank_data['business'] = business.pk
                bank_serializer = RetailerBankDetailsSerializer(data=bank_data)
                
                if bank_serializer.is_valid():
                    business = bank_serializer.save()
                    response_data[SUCCESS] = CREATED_SUCCESSFULL
                    response_data['unique_string'] = request.data['unique_string']
                    status_code = HTTP_200_SUCCESS
                else:
                    response_data[MESSAGE] = bank_serializer.errors
                    status_code = HTTP_API_ERROR
                    transaction.savepoint_rollback(sid)
            
            else:
                response_data[MESSAGE] = serializer.errors
                status_code = HTTP_API_ERROR
            
            return Response(response_data, status=status_code)

class RetailerBusinessUpdateView(generics.RetrieveUpdateAPIView):
    '''
    Business create api 
    '''
    serializer_class = RetailerBusinessCreateSerializer

    def get_object(self):
        return RetailerBusiness.objects.get(pk=self.kwargs['id'], is_active=True)

    def retrieve(self, *args, **kwargs):
        '''Retrieve'''
        try:
            return super(RetailerBusinessUpdateView, self).retrieve(*args, **kwargs)
        except (Http404, RetailerBusiness.DoesNotExist):
            return Response({MESSAGE: RETAILER_BUSINESS_NOT_FOUND}, status=HTTP_API_ERROR)
    
    def patch(self, request, *args, **kwargs):
        '''Partial update object'''
        response_data = {}
        instance = self.get_object()
        
        serializer = RetailerBusinessCreateSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            sid = transaction.savepoint()
            business = serializer.save()
            response = serializer.data
            
            bank_data = request.data.pop('bank_details')
            bank_data['business'] = instance.pk
            bank_serializer = RetailerBankDetailsSerializer(instance.bank_details, data=bank_data)
            if bank_serializer.is_valid():
                bank_serializer.save()
            else:
                response_data[MESSAGE] = bank_serializer.errors
                transaction.savepoint_rollback(sid)
                return Response(response_data, status=HTTP_API_ERROR)
            response_data[SUCCESS] = REQUEST_SUCCESSFULL
            return Response(response_data, status=HTTP_200_SUCCESS)
        else:
            response_data[MESSAGE] = serializer.errors
            return Response(response_data, status=HTTP_API_ERROR)


class ListLicensingRegion(generics.ListAPIView):
    '''
    LicensingRegion list api 
    '''
    serializer_class = LicensingRegionSerializer
    queryset = LicensingRegion.objects.filter(is_active=True).order_by('name')


class GetUpdateStoreView(generics.RetrieveUpdateAPIView):
    '''
    Business create api 
    '''
    serializer_class = StoreUpdateGetSerializer

    def get_object(self):
        return Store.objects.get(pk=self.kwargs['store_id'])
    
    def retrieve(self, *args, **kwargs):
        '''Retrieve'''
        try:
            return super(GetUpdateStoreView, self).retrieve(*args, **kwargs)
        except (Http404, RetailerBusiness.DoesNotExist):
            return Response({MESSAGE: STORE_NOT_FOUND}, status=HTTP_API_ERROR)
    
    def patch(self, request, *args, **kwargs):
        '''Partial update object'''
        response_data = {}
        instance = self.get_object()
        
        serializer = StoreUpdateGetSerializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            business = serializer.save()
            response = serializer.data
            response_data[SUCCESS] = REQUEST_SUCCESSFULL
            return Response(response_data, status=HTTP_200_SUCCESS)
        else:
            response_data[MESSAGE] = serializer.errors
            return Response(response_data, status=HTTP_API_ERROR)

class RetailerBusinessListView(generics.ListAPIView):
    serializer_class = RetailerBusinessListSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return RetailerBusiness.objects.filter(retailer_id=self.kwargs['retailer_id']).order_by('-id')


class DeactivateBusinessStoreView(generics.UpdateAPIView):
    serializer_class = StoreUpdateGetSerializer

    def patch(self, request, *args, **kwargs):
        response_data = {}
        
        if 'business_id' in self.kwargs.keys():
            business_vars = Q(pk=self.kwargs['business_id'])
            store_vars = Q(retailer_business=self.kwargs['business_id'])
        elif 'retailer_id' in self.kwargs.keys():
            business_vars = Q(retailer_id=self.kwargs['retailer_id'])
            store_vars = Q(retailer_business__retailer_id=self.kwargs['retailer_id'])
        
        RetailerBusiness.objects.filter(business_vars).update(is_active=request.data['is_active'])
        stores = Store.objects.filter(store_vars)
        stores.update(is_active=request.data['is_active'])
        
        response_data[SUCCESS] = REQUEST_SUCCESSFULL
        response_data['stores'] = stores.values_list('id', flat=True)

        return Response(response_data, status=HTTP_200_SUCCESS)


class DeactivateStoreView(generics.UpdateAPIView):
    serializer_class = StoreUpdateGetSerializer

    def patch(self, request, *args, **kwargs):
        response_data = {}
        
        stores = Store.objects.filter(id=self.kwargs['store_id'])
        stores.update(is_active=request.data['is_active'])
        
        response_data[SUCCESS] = REQUEST_SUCCESSFULL
        response_data['stores'] = stores.values_list('id', flat=True)

        return Response(response_data, status=HTTP_200_SUCCESS)

class AwaitingApprovalStoresView(generics.ListAPIView):
    '''
    Store list api 
    '''
    def get(self, request, *args, **kwargs):
        _ = self.__class__.__name__
        data = []
        stores_list = Store.objects.filter(store_status=Store.AWAITING_APPROVAL).distinct('retailer_business__retailer_id')
        for store in stores_list:
            stores = Store.objects.filter(retailer_business__retailer_id=store.retailer_business.retailer_id).aggregate(
                total_stores=Count('id'),
                    approved_stores=Sum(
                        Case(When(store_status=Store.APPROVED, then=1),
                        default=Value(0),
                        output_field=IntegerField())),
                    rejected_stores=Sum(
                        Case(When(store_status=Store.REJECTED, then=1),
                        default=Value(0),
                        output_field=IntegerField())),
                    awaiting_approval_stores=Sum(
                        Case(When(store_status=Store.AWAITING_APPROVAL, then=1),
                        default=Value(0),
                        output_field=IntegerField()))
                    )
            total_business = RetailerBusiness.objects.filter(retailer_id=store.retailer_business.retailer_id).count()
            stats_obj = {
                "total_stores": stores['total_stores'] if stores['total_stores'] else 0,
                "approved_stores": stores['approved_stores'] if stores['approved_stores'] else 0,
                "rejected_stores": stores['rejected_stores'] if stores['rejected_stores'] else 0,
                "total_business": total_business,
                "awaiting_approval_stores": stores['awaiting_approval_stores'] if stores['awaiting_approval_stores'] else 0,
                'retailer_id': store.retailer_business.retailer_id,
            }
            data.append(stats_obj)
        return Response(data)


class RetailerAwaitingApprovalStoreView(generics.ListAPIView):
    '''
    Store list api 
    '''
    serializer_class = AllStoreSerializers
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return Store.objects.filter(store_status=Store.AWAITING_APPROVAL,
                                    retailer_business__retailer_id=self.kwargs['retailer_id'])


class RetailersWhoHaveStoresView(generics.ListAPIView):
    '''
    Retailers View
    '''
    serializer_class = RetailerStoreMiniSerializer

    def get_queryset(self):
        _ = self.__class__.__name__
        return Store.objects.all().order_by('-retailer_business__retailer_id', '-id').distinct('retailer_business__retailer_id')


class RetailersStoresCountView(generics.CreateAPIView):
    '''
    Store list api 
    '''
    serializer_class = AllStoreSerializers
    pagination_class = CustomPagination
    

    def post(self, request, *args, **kwargs):
        _ = self
        requested_data = self.request.data

        approved_store_list = Store.objects.filter(retailer_business__retailer_id__in=self.request.data.get('retailer_ids'),
                                                   store_status=Store.APPROVED).order_by('-id')
        approved_filter_obj = RetailerStoreFilter(requested_data, queryset=approved_store_list)

        approved_stores = approved_filter_obj.qs.count()

        return Response(OrderedDict([
            ('approved_stores', approved_stores)
        ]))

class RetailersBusinessCountView(generics.CreateAPIView):
    '''
    Store list api 
    '''
    def post(self, request, *args, **kwargs):
        _ = self
        data = []
        for retailer_id in self.request.data.get('retailer_ids'):
            business_count = RetailerBusiness.objects.filter(retailer_id=retailer_id, is_active=True).count()
            stats_obj = {
                "business_count": business_count,
                'retailer_id': retailer_id,
            }
            data.append(stats_obj)
        return Response(data)


class TargetRetailerStoreStats(generics.ListAPIView):
    '''
    Target Retailer Store Stats
    '''
    def get(self, request, *args, **kwargs):
        _ = self.__class__.__name__
        stores = Store.objects.filter(is_active=True)
        total_retailers = stores.distinct('retailer_business__retailer_id').count()
        stats_obj = {
            "total_stores": stores.count(),
            "total_retailers": total_retailers,
        }
        return Response(stats_obj)

class UpdateSelfBilliingStatus(generics.ListAPIView):
    '''
    Target Retailer Store Stats
    '''
    def get(self, request, *args, **kwargs):
        try:
            business = RetailerBusiness.objects.get(unique_string__iexact=self.kwargs['unique_string'], is_billing_agreed=False)
            business.is_billing_agreed = True
            business.unique_string = get_random_string(length=32)
            business.save()
            business_obj = RetailerBusinessCreateSerializer(business).data
            stats_obj = {
                "business": business_obj
            }
        except RetailerBusiness.DoesNotExist:
            stats_obj = {
                "message": 'Business not found'
            }
        return Response(stats_obj)
