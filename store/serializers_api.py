''' Serializers '''
from rest_framework import serializers

from .models import Store


class StoreSerializers(serializers.ModelSerializer):
    '''
    Store Serializers
    '''
    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id', 'name', 'address1',  'postcode', 'latitude', 'longitude' )


class StoreDetailSerializers(serializers.ModelSerializer):
    '''
    Store Serializers
    '''
    licensing_region_name = serializers.CharField(source='licensing_region.name')
    class Meta:
        ''' Meta information serializer'''
        model = Store
        fields = ('id', 'name', 'address1', 'address2', 'postcode', 'fascia_display_name', 'wholesaler_name', 'epos_display_name', 'is_postoffice', 'is_lottery', 'is_paypoint', 'is_bakeoff', 'is_hotfood',
                    'licensing_status', 'licensing_region_name', 'average_weekly_turnover', 'average_weekly_footfall', 'average_basket_spend', 'store_size', 'fascia_name', 'epos_name')

    def to_representation(self, *args, **kwargs):
        instance = super(StoreDetailSerializers, self).to_representation(*args, **kwargs)
        if instance['fascia_display_name'].lower()=='other':
            instance['fascia_display_name']=instance['fascia_name']
        if instance['epos_display_name'].lower()=='other':
            instance['epos_display_name']=instance['epos_name']
        instance.pop('fascia_name')
        instance.pop('epos_name')
        return instance
