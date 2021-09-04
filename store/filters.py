'''filters.py'''

import django_filters
from django_filters import CharFilter, NumberFilter
from django_filters.rest_framework import FilterSet

from .models import Store


class StoreFilter(FilterSet):
    fascia = NumberFilter()
    wholesaler = NumberFilter()
    county = NumberFilter()
    licensing_status = NumberFilter()
    forecourt = NumberFilter()
    epos = NumberFilter()
    is_hotfood = NumberFilter()
    is_bakeoff = NumberFilter()
    is_paypoint = NumberFilter()
    is_lottery = NumberFilter()
    is_postoffice = NumberFilter()
    from_turnover = NumberFilter(method='filter_from_turnover')
    to_turnover = NumberFilter(method='filter_to_turnover')
    from_footfall = NumberFilter(method='filter_from_footfall')
    to_footfall = NumberFilter(method='filter_to_footfall')
    from_size = NumberFilter(method='filter_from_size')
    to_size = NumberFilter(method='filter_to_size')
    from_avg_basket = NumberFilter(method='filter_from_avg_spend')
    to_avg_basket = NumberFilter(method='filter_to_avg_spend')

    class Meta:
        model = Store
        fields = [
            'fascia',
            'wholesaler',
            'county',
            'forecourt',
            'licensing_status',
            'epos',
            'from_turnover',
            'to_turnover',
            'from_footfall',
            'to_footfall',
            'from_size',
            'to_size',
            'from_avg_basket',
            'to_avg_basket',
            'is_hotfood',
            'is_bakeoff',
            'is_paypoint',
            'is_lottery',
            'is_postoffice'
        ]

    def filter_from_turnover(self, queryset, name, value):
        '''
        from turnover filter 
        '''
        _ = self.__class__.__name__
        return queryset.filter(average_weekly_turnover__gte=value)
    
    def filter_to_turnover(self, queryset, name, value):
        '''
        to turnover filter 
        '''
        _ = self.__class__.__name__
        return queryset.filter(average_weekly_turnover__lte=value)
    
    def filter_from_footfall(self, queryset, name, value):
        '''
        from average_weekly_footfall filter 
        '''
        _ = self.__class__.__name__
        return queryset.filter(average_weekly_footfall__gte=value)
    
    
    def filter_to_footfall(self, queryset, name, value):
        '''
        to average_weekly_footfall filter 
        '''
        _ = self.__class__.__name__
        return queryset.filter(average_weekly_footfall__lte=value)
    
    def filter_from_size(self, queryset, name, value):
        '''
        from store_size filter 
        '''
        _ = self.__class__.__name__
        return queryset.filter(store_size__gte=value)
    
    def filter_to_size(self, queryset, name, value):
        '''
        to store_size filter 
        '''
        _ = self.__class__.__name__
        return queryset.filter(store_size__lte=value)
    
    def filter_from_avg_spend(self, queryset, name, value):
        '''
        from average_basket_spend filter 
        '''
        _ = self.__class__.__name__
        return queryset.filter(average_basket_spend__gte=value)
    
    def filter_to_avg_spend(self, queryset, name, value):
        '''
        to average_basket_spend filter 
        '''
        _ = self.__class__.__name__
        return queryset.filter(average_basket_spend__lte=value)


class RetailerStoreFilter(StoreFilter):
    licensing_region = NumberFilter()

    class Meta:
        model = Store
        fields = [
            'fascia',
            'wholesaler',
            'county',
            'forecourt',
            'licensing_status',
            'epos',
            'from_turnover',
            'to_turnover',
            'from_footfall',
            'to_footfall',
            'from_size',
            'to_size',
            'from_avg_basket',
            'to_avg_basket',
            'licensing_region',
        ]



class StoreCountFilter(object):

    def get_store_count(self, queryset, query_params):
        _ = self.__class__.__name__
        if query_params['epos']:
            queryset = queryset.filter(epos__id=query_params['epos'])

        if query_params['fascia']:
            queryset = queryset.filter(fascia__id=query_params['fascia'])

        if query_params['wholesaler']:
            queryset = queryset.filter(wholesaler__id=query_params['wholesaler'])

        if query_params['county']:
            queryset = queryset.filter(county__id=query_params['county'])

        if query_params['forecourt']:
            queryset = queryset.filter(forecourt=query_params['forecourt'])

        if query_params['licensed']:
            queryset = queryset.filter(licensing_status=query_params['licensed'])

        if query_params['from_turnover'] and query_params['to_turnover']:
            queryset = queryset.filter(average_weekly_turnover__range=(query_params['from_turnover'], query_params['to_turnover']))
        
        if query_params['from_avg_basket'] and query_params['to_avg_basket']:
            queryset = queryset.filter(average_basket_spend__range=(query_params['from_avg_basket'], query_params['to_avg_basket']))
       
        if query_params['from_size'] and query_params['to_size']:
            queryset = queryset.filter(store_size__range=(query_params['from_size'], query_params['to_size']))

        if query_params['from_footfall'] and query_params['to_footfall']:
            queryset = queryset.filter(average_weekly_footfall__range=(query_params['from_footfall'], query_params['to_footfall']))

        return queryset.count()
