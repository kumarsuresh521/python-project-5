'''urls configurations for rest api requests'''
from django.conf.urls import url

from .api import ListStoreView, EvidenceStoreListingView, StoreView, StaffDetailStoresListingView

urlpatterns = [
    url(r'^stores/(?P<user_id>\d+)/$', ListStoreView.as_view(), name="store_list"),
    url(r'^store/(?P<store_id>\d+)/$', StoreView.as_view(), name="store_detail"),
    url(r'^evidence-store/$', EvidenceStoreListingView.as_view(), name="evidence_store"),
    url(r'^staff-detail-store/$', StaffDetailStoresListingView.as_view(), name="staff_detail_store"),   
]
