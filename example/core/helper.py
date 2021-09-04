from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .constants import ADMIN_PAGE_SIZE


class CustomPagination(PageNumberPagination):
    page_size = ADMIN_PAGE_SIZE

    def get_paginated_response(self, data):
        next_page = int(self.page.number) + 1 if self.page.has_next() else None
        previous_page = int(self.page.number) - 1 if self.page.has_previous() else None
        return Response(OrderedDict([
            ('next', next_page),
            ('previous', previous_page),
            ('total_count', self.page.paginator.count),
            ('results', data)
        ]))
