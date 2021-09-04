'''
Store Models
'''

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from pgcrypto import fields

from .message import *


class RetailerBusiness(models.Model):
    '''
    Retailer Business
    '''
    retailer_id = models.SmallIntegerField() # user id for retailer
    name = models.CharField(unique=True, max_length=55, error_messages={'unique': UNIQUE_BUSINESS_NAME})
    address1 = models.CharField(max_length=150)
    address2 = models.CharField(max_length=150, null=True, blank=True)
    postcode = models.CharField(max_length=150, null=True, blank=True)
    town = models.CharField(max_length=150, null=True, blank=True)
    county = models.ForeignKey('County', on_delete=models.CASCADE)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)
    company_number = models.CharField(unique=True, max_length=150, error_messages={'unique': UNIQUE_COMPANY_NUMBER})
    vat_number = models.CharField(unique=True, max_length=150, error_messages={'unique': UNIQUE_VAT_NUMBER})
    notes = models.TextField(max_length=500)
    unique_string = models.CharField(max_length=244, null=True, blank=True)
    is_limited = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_billing_agreed = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)


class BankDetails(models.Model):
    business = models.OneToOneField(RetailerBusiness, on_delete=models.CASCADE, related_name='bank_details')
    bank_name = models.CharField(max_length=150, null=True, blank=True)
    sort_code1 = models.CharField(max_length=4, null=True, blank=True)
    sort_code2 = models.CharField(max_length=3, null=True, blank=True)
    sort_code3 = models.CharField(max_length=4, null=True, blank=True)
    account_number = models.CharField(max_length=25, null=True, blank=True)

class Store(models.Model):
    '''
    Store models'''
    YES = 1
    NO = 2
    LICENSING_CHOICES = (
        (YES, 'Yes'),
        (NO, 'No'),
    )

    AWAITING_APPROVAL = 1
    APPROVED = 2
    REJECTED = 3

    STATUS_CHOICES = (
        (AWAITING_APPROVAL, 'Awaiting Approval'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        )
    
    retailer_business = models.ForeignKey(RetailerBusiness, related_name= 'stores')
    name = models.CharField(unique=True, max_length=254, null=True, blank=True, error_messages={'unique': UNIQUE_STORE_NAME})
    address1 = models.TextField(max_length=150)
    address2 = models.TextField(max_length=150, null=True, blank=True)
    town = models.CharField(max_length=150)
    postcode = models.CharField(max_length=15)
    latitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    longitude = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
    contact_name = models.CharField(max_length=150, null=True, blank=True)
    contact_number = models.CharField(max_length=150, null=True, blank=True)
    fascia = models.ForeignKey('Fascia', on_delete=models.CASCADE)
    fascia_name = models.CharField(max_length=50, blank=True, null=True)
    wholesaler = models.ForeignKey('Wholesaler', on_delete=models.CASCADE)
    county = models.ForeignKey('County', on_delete=models.CASCADE)
    country = models.ForeignKey('Country', on_delete=models.CASCADE)
    licensing_status = models.SmallIntegerField(choices=LICENSING_CHOICES, default=YES)
    licensing_region = models.ForeignKey('LicensingRegion', on_delete=models.CASCADE)
    average_weekly_turnover = models.IntegerField(default=0, validators=[MaxValueValidator(999999), MinValueValidator(0)])
    average_weekly_footfall = models.IntegerField(default=0, validators=[MaxValueValidator(999999), MinValueValidator(0)])
    average_basket_spend = models.FloatField(default=0, validators=[MaxValueValidator(999999), MinValueValidator(0)])
    store_size = models.IntegerField(help_text="Sq Ft", default=0, validators=[MaxValueValidator(999999), MinValueValidator(0)])
    epos = models.ForeignKey('EposSystem', on_delete=models.CASCADE)
    epos_name = models.CharField(max_length=50, null=True, blank=True)
    admin_notes = models.TextField(null=True, blank=True)
    retailer_notes = models.TextField(null=True, blank=True)
    is_postoffice = models.BooleanField(default=True)
    is_lottery = models.BooleanField(default=True)
    is_paypoint = models.BooleanField(default=True)
    is_bakeoff = models.BooleanField(default=True)
    is_hotfood = models.BooleanField(default=True)
    store_status = models.SmallIntegerField(choices=STATUS_CHOICES, default=AWAITING_APPROVAL)
    is_active = models.BooleanField(default=True)
    another_store_available = models.BooleanField(default=False)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)

    @property
    def retailer_business_name(self):
        return self.retailer_business.name

    @property
    def retailer_id(self):
        return self.retailer_business.retailer_id

    @property
    def fascia_display_name(self):
        return self.fascia.name
    
    @property
    def wholesaler_name(self):
        return self.wholesaler.name
    
    @property
    def epos_display_name(self):
        return self.epos.name
    
    @property
    def licensing_region_name(self):
        return self.licensing_region.name
    
    @property
    def licensing_status_name(self):
        return self.get_licensing_status_display()


class Fascia(models.Model):
    '''
    Fascia model
    '''
    wholesaler = models.ForeignKey('Wholesaler')
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)


class Wholesaler(models.Model):
    '''
    Wholesaler model
    '''
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)


class County(models.Model):
    '''
    County model
    '''
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
    country_id = models.IntegerField(null=True, blank=True)


class Country(models.Model):
    '''
    Country model
    '''
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)


class StoreFormat(models.Model):
    '''
    store format like CTN / Convenience / Transient 
    '''
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)


class LicensingRegion(models.Model):
    '''
    licensing status like Licensed/Unlicensed
    '''
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)


class EposSystem(models.Model):
    '''
    EposSystem class
    '''
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    create_date = models.DateTimeField(auto_now_add=True)
    modify_date = models.DateTimeField(auto_now=True)
