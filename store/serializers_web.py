''' Serializers '''
from django.core.exceptions import ValidationError
from django.db.models import Count, Sum
from example.core.utils import VerifyBankAccount
from rest_framework import serializers

from .filters import StoreCountFilter
from .models import (BankDetails, Country, County, EposSystem, Fascia,
                     LicensingRegion, RetailerBusiness, Store, Wholesaler)


def lower(value):
    if value is not None or value !='':
        return value.lower()
    else:
        return value

class StoreSerializers(serializers.ModelSerializer):
    '''
    Store Serializer
    '''
    business = serializers.SerializerMethodField()
    retailer_id = serializers.SerializerMethodField()

    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id', 'name', 'address1', 'address2', 'town', 'postcode', 'county', 'country',
        'fascia', 'wholesaler', 'epos', 'licensing_region', 'fascia_display_name', 'epos_display_name',
        'fascia_name', 'wholesaler_name', 'epos_name', 'licensing_region_name', 'latitude', 'longitude',
        'average_weekly_turnover', 'average_weekly_footfall', 'average_basket_spend', 'store_size',
        'licensing_status_name', 'business', 'retailer_id', 'retailer_business', 'is_postoffice', 'is_lottery', 'is_paypoint', 
        'is_bakeoff', 'is_hotfood', 'licensing_status', 'admin_notes', 'retailer_notes', 'is_active', 'store_status',
         'contact_name', 'contact_number', 'another_store_available')

    def get_retailer_id(self, obj):
        _ = self.__class__.__name__
        return obj.retailer_business.retailer_id

    def get_business(self, obj):
        ''' Return Media assets serialized data/object'''
        _ = self.__class__.__name__
        return RetailerBusinessFullSerializer(obj.retailer_business, many=False).data


class AllStoreSerializers(serializers.ModelSerializer):
    '''
    Store Serializer
    '''
    business = serializers.SerializerMethodField()
    retailer_id = serializers.SerializerMethodField()
    activation_percentage = serializers.SerializerMethodField()
    optin_percentage = serializers.SerializerMethodField()

    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id', 'name', 'address1', 'address2', 'town', 'postcode', 'county', 'country', 'contact_name', 
        'fascia', 'wholesaler', 'epos', 'licensing_region', 'fascia_display_name', 'epos_display_name', 'contact_number',
        'fascia_name', 'wholesaler_name', 'epos_name', 'licensing_region_name', 'retailer_notes', 'latitude', 'longitude',
        'average_weekly_turnover', 'average_weekly_footfall', 'average_basket_spend', 'store_size', 'another_store_available',
        'licensing_status_name', 'business', 'retailer_id', 'retailer_business', 'is_postoffice', 'is_lottery', 'admin_notes',
        'is_paypoint', 'is_bakeoff', 'is_hotfood', 'activation_percentage', 'optin_percentage', 'is_active', 'store_status')

    def get_retailer_id(self, obj):
        _ = self.__class__.__name__
        return obj.retailer_business.retailer_id

    def get_activation_percentage(self, obj):
        _ = self.__class__.__name__
        return 5

    def get_optin_percentage(self, obj):
        _ = self.__class__.__name__
        return 5

    def get_business(self, obj):
        ''' Return Media assets serialized data/object'''
        _ = self.__class__.__name__
        return RetailerBusinessFullSerializer(obj.retailer_business, many=False).data


class FasciaSerializers(serializers.ModelSerializer):
    '''
    Fascia Serializer
    '''
    class Meta:
        ''' Meta information serializer'''
        model = Fascia
        fields = ('id', 'name')


class WholesalerSerializers(serializers.ModelSerializer):
    '''
    Wholesaler Serializers
    '''
    class Meta:
        ''' Meta information serializer'''
        model = Wholesaler
        fields = ('id', 'name')


class EposSystemSerializers(serializers.ModelSerializer):
    '''
    EposSystem Serializers
    '''
    class Meta:
        ''' Meta information serializer'''
        model = EposSystem
        fields = ('id', 'name')


class CountySerializers(serializers.ModelSerializer):
    '''
    EposSystem Serializers
    '''
    class Meta:
        ''' Meta information serializer'''
        model = County
        fields = ('id', 'name')


class CountrySerializers(serializers.ModelSerializer):
    '''
    Country Serializers
    '''
    class Meta:
        ''' Meta information serializer'''
        model = Country
        fields = ('id', 'name')


class RetailerBusinessStoreSerializer(serializers.ModelSerializer):
    '''
    Retailer Business Store Serializer
    '''
    business_count = serializers.SerializerMethodField()
    total_stores = serializers.SerializerMethodField()

    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id', 'retailer_business', 'business_count', 'retailer_id', 'total_stores', 'is_active')

    def get_business_count(self, obj):
        _ = self.__class__.__name__
        return RetailerBusiness.objects.filter(retailer_id=obj.retailer_id).count()

    def get_total_stores(self, obj):
        _ = self.__class__.__name__
        total_stores = RetailerBusiness.objects.filter(retailer_id=obj.retailer_id).aggregate(total_stores=Count('stores'))
        return total_stores['total_stores']



class RetailerStoreSerializer(serializers.ModelSerializer):
    '''
    Retailer Store Serializer
    '''
    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id', 'retailer_business', 'retailer_id', 'total_stores', 'matched_stores', 'retailer_business_name', 'is_active')

    total_stores = serializers.SerializerMethodField()
    matched_stores = serializers.SerializerMethodField()
    
    def get_total_stores(self, obj):
        _ = self.__class__.__name__
        return obj.retailer_business.stores.filter(is_active=True).count()

    def get_matched_stores(self, obj):
        
        query_params = self.context['request'].query_params
        queryset = obj.retailer_business.stores.filter(is_active=True)
        
        store_count_obj = StoreCountFilter()
        store_count = store_count_obj.get_store_count(queryset, query_params)

        return store_count


class BusinessStoreSerializer(serializers.ModelSerializer):
    '''
    Business Store Serializer
    '''
    is_matched_criteria = serializers.SerializerMethodField()
    is_searched_criteria = serializers.SerializerMethodField()
    licensing_status = serializers.SerializerMethodField()
    forecourt = serializers.SerializerMethodField()
    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id', 'name', 'address1', 'postcode', 'town', 'wholesaler_name', 'fascia_name', 'fascia_display_name', 'latitude', 'longitude',
        'average_weekly_turnover', 'average_weekly_footfall', 'average_basket_spend', 'retailer_business', 'contact_name', 'contact_number',
        'licensing_status', 'store_size', 'forecourt', 'licensing_region_name', 'epos_name', 'epos_display_name', 'is_matched_criteria',
        'is_searched_criteria', 'is_postoffice', 'is_lottery', 'is_paypoint', 'is_bakeoff', 'is_hotfood', 'is_active', 'store_status', 'another_store_available')

    def get_is_matched_criteria(self, instance):
        if instance.id in self.context['matched_stores']:
            return True
        return False
    
    def get_is_searched_criteria(self, instance):
        _ = self.__class__.__name__
        if self.context['search_text'] is not None and self.context['search_text'] != '':
            search_text = self.context['search_text'].lower()
            match_list = []
            
            if instance.postcode is not None and instance.postcode != '':
                match_list.append(search_text in instance.postcode.lower())
            
            if instance.name is not None and instance.name != '':
                match_list.append(search_text in instance.name.lower())
            
            if instance.address1 is not None and instance.address1 != '':
                match_list.append(search_text in instance.address1.lower())
            
            if instance.address2 is not None and instance.address2 != '':
                match_list.append(search_text in instance.address2.lower())
            
            if instance.town is not None and instance.town != '':
                match_list.append(search_text in instance.town.lower())
            
            if instance.fascia.name is not None and instance.fascia.name != '':
                match_list.append(search_text in instance.fascia.name.lower())
            
            if instance.county.name is not None and instance.county.name != '':
                match_list.append(search_text in instance.county.name.lower())
            
            if instance.wholesaler.name is not None and instance.wholesaler.name != '':
                match_list.append(search_text in instance.wholesaler.name.lower())
            
            if instance.retailer_business.name is not None and instance.retailer_business.name != '':
                match_list.append(search_text in instance.retailer_business.name.lower())
            

            if True in match_list:
                return True
        return False
    
    def get_licensing_status(self, obj):
        _ = self.__class__.__name__
        return obj.get_licensing_status_display()
    
    def get_forecourt(self, obj):
        _ = self.__class__.__name__
        return obj.get_licensing_status_display()


class FilterBusinessStoreSerializer(serializers.ModelSerializer):
    '''
    Business Store Serializer
    '''
    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id',)


class SearchStoreSerializer(serializers.ModelSerializer):
    '''
    Serializer to search campaign
    '''
    total_stores = serializers.SerializerMethodField()
    matched_stores = serializers.SerializerMethodField()
    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id', 'retailer_business', 'retailer_id', 'total_stores', 'matched_stores', 'retailer_business_name', 'is_active')
    
    def get_total_stores(self, obj):
        _ = self.__class__.__name__
        return obj.retailer_business.stores.filter(is_active=True).count()

    def get_matched_stores(self, obj):
        _ = self.__class__.__name__
        return obj.retailer_business.stores.filter(is_active=True).count()

class RetailerBusinessSerializer(serializers.ModelSerializer):
    '''
    Serializer to Retailer Business
    '''
    total_stores = serializers.SerializerMethodField()
    class Meta:
        ''' Meta information serializer'''
        model = RetailerBusiness
        fields = ('id', 'name', 'total_stores')

    def get_total_stores(self, obj):
        _ = self.__class__.__name__
        return obj.stores.count()

class RetailerBusinessFullSerializer(serializers.ModelSerializer):
    '''
    Serializer to Retailer Business
    '''
    class Meta:
        ''' Meta information serializer'''
        model = RetailerBusiness
        fields = '__all__'

class RetailerBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        ''' Meta information serializer'''
        model = BankDetails
        fields = ('bank_name', 'sort_code1', 'sort_code2', 'sort_code3', 'account_number', 'business')

    def validate(self, validated_data):
        # check valid account number
        _ = self.__class__.__name__
        verify_bank_obj = VerifyBankAccount()
        params = {}
        params['SortCode'] = validated_data['sort_code1'] + validated_data['sort_code2'] + validated_data['sort_code3']
        params['AccountNumber'] = validated_data['account_number']
        response = verify_bank_obj.validate_account(params)

        if response['verify'] is False:
            raise ValidationError(response['message'])

        return validated_data

class RetailerBusinessCreateSerializer(serializers.ModelSerializer):
    '''
    serializer to create Retailer business    '''
    
    bank_details = RetailerBankDetailsSerializer(read_only=True)
    class Meta:
        ''' Meta information serializer'''
        model = RetailerBusiness
        fields = ('id', 'retailer_id', 'name', 'address1', 'address2', 'postcode', 'town', 'unique_string',
                  'county', 'country', 'company_number', 'vat_number', 'notes', 'bank_details', 'is_limited','is_active')


class LicensingRegionSerializer(serializers.ModelSerializer):

    class Meta:
        ''' Meta information serializer'''
        model = LicensingRegion
        fields = ('id', 'name')


class StoreUpdateGetSerializer(serializers.ModelSerializer):
    class Meta:
        ''' Meta information serializer '''
        model = Store
        fields = ('id', 'name', 'address1', 'address2', 'town', 'postcode', 'county', 'country', 'retailer_notes',
        'fascia', 'wholesaler', 'epos', 'licensing_region', 'fascia_display_name', 'epos_display_name', 'retailer_id',
        'fascia_name', 'wholesaler_name', 'epos_name', 'licensing_region_name', 'is_active', 'store_status', 'admin_notes',
        'average_weekly_turnover', 'average_weekly_footfall', 'average_basket_spend', 'store_size', 'licensing_status',
        'licensing_status_name', 'retailer_business', 'is_postoffice', 'is_lottery', 'is_paypoint', 'is_bakeoff', 'is_hotfood',
        'contact_name', 'contact_number', 'latitude', 'longitude', 'another_store_available',)


class RetailerBusinessListSerializer(serializers.ModelSerializer):
    county_name = serializers.CharField(source='county.name')
    country_name = serializers.CharField(source='country.name')
    bank_details = RetailerBankDetailsSerializer(read_only=True)
    class Meta:
        ''' Meta information serializer '''
        model = RetailerBusiness
        fields = ('id', 'is_active', 'retailer_id', 'name', 'address1', 'address2', 'postcode', 'town',
                  'county', 'country', 'company_number', 'vat_number', 'notes', 'bank_details',
                  'is_limited', 'country_name', 'county_name')

class RetailerStoreMiniSerializer(serializers.ModelSerializer):
    '''
    Retailer Store Serializer
    '''
    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id', 'retailer_business', 'retailer_id', 'is_active')
