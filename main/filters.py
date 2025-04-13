from django_filters import rest_framework as filters
from .models import NetworkNode



class NetworkNodeFilter(filters.FilterSet):
    product = filters.NumberFilter(
        method='filter_by_product',
        label='Фильтр по ID продукта'
    )

    def filter_by_product(self, queryset, name, value):
        return queryset.filter(products__id=value).distinct()

    country = filters.CharFilter(field_name='country', lookup_expr='iexact')

    class Meta:
        model = NetworkNode
        fields = ['product', 'country']
