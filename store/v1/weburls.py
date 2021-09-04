'''urls configurations for rest api requests'''
from django.conf.urls import url

from .web import *

urlpatterns = [
    url(r'^stores/$', ListStoreByIdView.as_view(), name="store_list"),
    url(r'^retailer-stores/$', ListStoreView.as_view(), name="retailer_store_list"),
    url(r'^stores-awaiting-approval/$', AwaitingApprovalStoresView.as_view(), name="stores_awaiting_approval"),
    url(r'^retailer-awaiting-approval-stores/(?P<retailer_id>.+)/$', RetailerAwaitingApprovalStoreView.as_view(), name="retailer_awaiting_approval_stores"),
    url(r'^stores-by-retailer/(?P<retailer_id>.+)/$', RetailerAllStoreView.as_view(), name="stores_by_retailer"),
    url(r'^add-store/$', CreateStoreView.as_view(), name="add_store"),
    url(r'^store/(?P<store_id>.+)$', GetUpdateStoreView.as_view(), name="get_update_store"),
    url(r'^search-store/$', SearchStore.as_view(), name="search_store"),
    url(r'^edit-store/(?P<id>.+)/$', UpdateStoreView.as_view(), name="edit_store"),
    url(r'^delete-store/(?P<id>.+)/$', DeleteStoreView.as_view(), name="delete_store"),
    url(r'^wholesaler/$', ListWholesalerView.as_view(), name="list_wholesaler"),
    url(r'^fascia/$', ListFasciaView.as_view(), name="list_fascia"),
    url(r'^epossystem/$', ListEposSystemView.as_view(), name="list_epos"),
    url(r'^county/$', ListCountyView.as_view(), name="list_county"),
    url(r'^country/$', ListCountryView.as_view(), name="list_country"),
    url(r'^retailer/$', ListRetailersView.as_view(), name="list_retailer"),
    url(r'^retailer-filter/$', ListRetailersBusinessView.as_view(), name="list_retailer_filter"),
    url(r'^business-list/$', RetailerBusinessList.as_view(), name="business_list"),
    url(r'^businessstores/(?P<id>.+)/$', ListBusinessStoresView.as_view(), name="business_stores"),
    url(r'^filter-business-stores/(?P<id>.+)/$', FilterBusinessStoresView.as_view(), name="filter_business_stores"),
    url(r'^retailer-business/$', RetailerBusinessView.as_view(), name="retailer_business"),
    url(r'^retailer-business-list/(?P<retailer_id>\d+)/$', RetailerBusinessListView.as_view(), name="retailer_business_list"),
    url(r'^retailer-business/(?P<id>.+)/$', RetailerBusinessUpdateView.as_view(), name="retailer_business_update"),
    url(r'^licensing-region/$', ListLicensingRegion.as_view(), name="licensing_region"),
    
    url(r'^deactivate-retailer-business/(?P<retailer_id>\d+)/$', DeactivateBusinessStoreView.as_view(), name="retailer_business_inactive"),
    url(r'^deactivate-business/(?P<business_id>\d+)/$', DeactivateBusinessStoreView.as_view(), name="business_inactive"),
    url(r'^deactivate-store/(?P<store_id>\d+)/$', DeactivateStoreView.as_view(), name="store_inactive"),
    url(r'^stores-retailer/$', RetailersWhoHaveStoresView.as_view(), name="stores_retailer"),
    url(r'^retailer-stats/$', RetailersStoresCountView.as_view(), name="retailer_stats"),
    url(r'^retailer-business-count/$', RetailersBusinessCountView.as_view(), name="retailer_business_count"),
    url(r'^target-retailer-store-stats/$', TargetRetailerStoreStats.as_view(), name="target_retailer_store_stats"),
    url(r'^update-self-billing-status/(?P<unique_string>\w+)/$', UpdateSelfBilliingStatus.as_view(), name="update_self_billing_status"),
]
